# src/core/ole_drag_drop.py - Soporte nativo de Windows OLE Drag & Drop (DoDragDrop e IDropTarget)
"""
Módulo para permitir arrastrar y soltar (Drag & Drop) nativo de Windows:
- Arrastrar desde el explorador de la app hacia Windows Explorer (mover/copiar).
- Arrastrar desde la app hacia programas externos como Nitro PDF, Word, Excel, Chrome (abrir archivo).
- Recibir archivos arrastrados internamente o desde Windows Explorer hacia el árbol de carpetas.
Implementado usando ctypes puro sobre las APIs COM de ole32 y shell32 de Windows (sin dependencias externas).
"""

import os
import ctypes
from ctypes import wintypes

# ─── Inicialización de librerías Win32 ──────────────────────────────────────────
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# Inicializar OLE en el hilo UI
ole32.OleInitialize(None)

# ─── Constantes COM y OLE ──────────────────────────────────────────────────────
S_OK = 0
S_FALSE = 1
E_NOTIMPL = -2147467263         # 0x80004001
E_NOINTERFACE = -2147467262     # 0x80004002
E_INVALIDARG = -2147024809      # 0x80070057
DV_E_FORMATETC = -2147221404    # 0x80040064

DRAGDROP_S_DROP = 0x00040100
DRAGDROP_S_CANCEL = 0x00040101
DRAGDROP_S_USEDEFAULTCURSORS = 0x00040102

DROPEFFECT_NONE = 0
DROPEFFECT_COPY = 1
DROPEFFECT_MOVE = 2
DROPEFFECT_LINK = 4

CF_HDROP = 15
CF_UNICODETEXT = 13
DVASPECT_CONTENT = 1
TYMED_HGLOBAL = 1
DATADIR_GET = 1

GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
GHND = GMEM_MOVEABLE | GMEM_ZEROINIT

MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002

# ─── Configuración de tipos y prototipos Win32 ──────────────────────────────────
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalFree.restype = wintypes.HGLOBAL
kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]

user32.RegisterClipboardFormatW.restype = wintypes.UINT
user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]

shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
shell32.DragQueryFileW.restype = wintypes.UINT

ole32.RegisterDragDrop.argtypes = [wintypes.HWND, wintypes.LPVOID]
ole32.RegisterDragDrop.restype = ctypes.c_long
ole32.RevokeDragDrop.argtypes = [wintypes.HWND]
ole32.RevokeDragDrop.restype = ctypes.c_long

ole32.DoDragDrop.argtypes = [
    wintypes.LPVOID,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD)
]
ole32.DoDragDrop.restype = ctypes.c_long

# Formatos registrados de Windows Shell
CF_PREFERREDDROPEFFECT = user32.RegisterClipboardFormatW("Preferred DropEffect")
CF_PERFORMEDDROPEFFECT = user32.RegisterClipboardFormatW("Performed DropEffect")
CF_PASTESUCCEEDED = user32.RegisterClipboardFormatW("Paste Succeeded")

# ─── Estructuras COM ────────────────────────────────────────────────────────────
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ]
    def to_bytes(self):
        return bytes(self)

IID_IUnknown = GUID(0x00000000, 0x0000, 0x0000, (wintypes.BYTE * 8)(0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46))
IID_IDataObject = GUID(0x0000010e, 0x0000, 0x0000, (wintypes.BYTE * 8)(0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46))
IID_IDropSource = GUID(0x00000121, 0x0000, 0x0000, (wintypes.BYTE * 8)(0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46))
IID_IDropTarget = GUID(0x00000122, 0x0000, 0x0000, (wintypes.BYTE * 8)(0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46))
IID_IEnumFORMATETC = GUID(0x00000103, 0x0000, 0x0000, (wintypes.BYTE * 8)(0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46))

class FORMATETC(ctypes.Structure):
    _fields_ = [
        ("cfFormat", wintypes.UINT),
        ("ptd", wintypes.LPVOID),
        ("dwAspect", wintypes.DWORD),
        ("lindex", wintypes.LONG),
        ("tymed", wintypes.DWORD)
    ]

class STGMEDIUM(ctypes.Structure):
    _fields_ = [
        ("tymed", wintypes.DWORD),
        ("hGlobal", wintypes.HANDLE),
        ("pUnkForRelease", wintypes.LPVOID)
    ]

ole32.ReleaseStgMedium.argtypes = [ctypes.POINTER(STGMEDIUM)]
ole32.ReleaseStgMedium.restype = None

class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL)
    ]

class POINTL(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG)
    ]

# Prototipos de métodos COM
QI_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(GUID), ctypes.POINTER(wintypes.LPVOID))
ADDREF_PROTO = ctypes.WINFUNCTYPE(wintypes.ULONG, wintypes.LPVOID)
RELEASE_PROTO = ctypes.WINFUNCTYPE(wintypes.ULONG, wintypes.LPVOID)

QUERYCONTINUE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.BOOL, wintypes.DWORD)
GIVEFEEDBACK_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.DWORD)

GETDATA_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(FORMATETC), ctypes.POINTER(STGMEDIUM))
GETDATAHERE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(FORMATETC), ctypes.POINTER(STGMEDIUM))
QUERYGETDATA_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(FORMATETC))
GETCANONICAL_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(FORMATETC), ctypes.POINTER(FORMATETC))
SETDATA_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(FORMATETC), ctypes.POINTER(STGMEDIUM), wintypes.BOOL)
ENUMFORMATETC_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.LPVOID))
DADVISE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(FORMATETC), wintypes.DWORD, wintypes.LPVOID, ctypes.POINTER(wintypes.DWORD))
DUNADVISE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.DWORD)
ENUMDADVISE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(wintypes.LPVOID))

NEXT_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.ULONG, ctypes.POINTER(FORMATETC), ctypes.POINTER(wintypes.ULONG))
SKIP_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.ULONG)
RESET_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID)
CLONE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, ctypes.POINTER(wintypes.LPVOID))

# En 64-bit y 32-bit, POINTL (2 x LONG de 32 bits = 64 bits) empaquetado como un escalar
# ctypes.c_uint64 evita problemas de alineación de pila (stack mismatch en libffi) con el 5° argumento (pdwEffect).
DRAGENTER_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, ctypes.c_uint64, ctypes.POINTER(wintypes.DWORD))
DRAGOVER_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.DWORD, ctypes.c_uint64, ctypes.POINTER(wintypes.DWORD))
DRAGLEAVE_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID)
DROP_PROTO = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, ctypes.c_uint64, ctypes.POINTER(wintypes.DWORD))

# VTables e implementaciones
class IDataObjectVtbl(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", QI_PROTO),
        ("AddRef", ADDREF_PROTO),
        ("Release", RELEASE_PROTO),
        ("GetData", GETDATA_PROTO),
        ("GetDataHere", GETDATAHERE_PROTO),
        ("QueryGetData", QUERYGETDATA_PROTO),
        ("GetCanonicalFormatEtc", GETCANONICAL_PROTO),
        ("SetData", SETDATA_PROTO),
        ("EnumFormatEtc", ENUMFORMATETC_PROTO),
        ("DAdvise", DADVISE_PROTO),
        ("DUnadvise", DUNADVISE_PROTO),
        ("EnumDAdvise", ENUMDADVISE_PROTO),
    ]

class IDataObjectImpl(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IDataObjectVtbl))]

class IDropSourceVtbl(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", QI_PROTO),
        ("AddRef", ADDREF_PROTO),
        ("Release", RELEASE_PROTO),
        ("QueryContinueDrag", QUERYCONTINUE_PROTO),
        ("GiveFeedback", GIVEFEEDBACK_PROTO),
    ]

class IDropSourceImpl(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IDropSourceVtbl))]

class IEnumFORMATETCVtbl(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", QI_PROTO),
        ("AddRef", ADDREF_PROTO),
        ("Release", RELEASE_PROTO),
        ("Next", NEXT_PROTO),
        ("Skip", SKIP_PROTO),
        ("Reset", RESET_PROTO),
        ("Clone", CLONE_PROTO),
    ]

class IEnumFORMATETCImpl(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IEnumFORMATETCVtbl))]

class IDropTargetVtbl(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", QI_PROTO),
        ("AddRef", ADDREF_PROTO),
        ("Release", RELEASE_PROTO),
        ("DragEnter", DRAGENTER_PROTO),
        ("DragOver", DRAGOVER_PROTO),
        ("DragLeave", DRAGLEAVE_PROTO),
        ("Drop", DROP_PROTO)
    ]

class IDropTargetImpl(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IDropTargetVtbl))]


# ─── Enumerador de Formatos de Portapapeles (IEnumFORMATETC) ───────────────────
class EnumFormatEtc:
    def __init__(self, formats):
        self.formats = list(formats)
        self.index = 0
        self.ref_count = 1

        self.vtbl = IEnumFORMATETCVtbl(
            QueryInterface=QI_PROTO(self._QueryInterface),
            AddRef=ADDREF_PROTO(self._AddRef),
            Release=RELEASE_PROTO(self._Release),
            Next=NEXT_PROTO(self._Next),
            Skip=SKIP_PROTO(self._Skip),
            Reset=RESET_PROTO(self._Reset),
            Clone=CLONE_PROTO(self._Clone)
        )
        self.impl = IEnumFORMATETCImpl(lpVtbl=ctypes.pointer(self.vtbl))

    @property
    def ptr(self):
        return ctypes.cast(ctypes.pointer(self.impl), wintypes.LPVOID)

    def _QueryInterface(self, this, riid_ptr, ppv_ptr):
        if not riid_ptr or not ppv_ptr:
            return E_INVALIDARG
        riid = riid_ptr.contents.to_bytes()
        if riid in (IID_IUnknown.to_bytes(), IID_IEnumFORMATETC.to_bytes()):
            ppv_ptr[0] = this
            self._AddRef(this)
            return S_OK
        ppv_ptr[0] = None
        return E_NOINTERFACE

    def _AddRef(self, this):
        self.ref_count += 1
        return self.ref_count

    def _Release(self, this):
        self.ref_count -= 1
        return self.ref_count

    def _Next(self, this, celt, rgelt_ptr, pceltFetched_ptr):
        if not rgelt_ptr:
            return E_INVALIDARG
        fetched = 0
        while fetched < celt and self.index < len(self.formats):
            cf = self.formats[self.index]
            rgelt_ptr[fetched].cfFormat = cf
            rgelt_ptr[fetched].ptd = None
            rgelt_ptr[fetched].dwAspect = DVASPECT_CONTENT
            rgelt_ptr[fetched].lindex = -1
            rgelt_ptr[fetched].tymed = TYMED_HGLOBAL
            fetched += 1
            self.index += 1
        if pceltFetched_ptr:
            pceltFetched_ptr[0] = fetched
        return S_OK if fetched == celt else S_FALSE

    def _Skip(self, this, celt):
        self.index = min(self.index + celt, len(self.formats))
        return S_OK if self.index < len(self.formats) else S_FALSE

    def _Reset(self, this):
        self.index = 0
        return S_OK

    def _Clone(self, this, ppenum_ptr):
        if not ppenum_ptr:
            return E_INVALIDARG
        new_enum = EnumFormatEtc(self.formats)
        new_enum.index = self.index
        ppenum_ptr[0] = new_enum.ptr
        return S_OK


# ─── Fuente de Drag & Drop (IDropSource) ───────────────────────────────────────
class DropSource:
    def __init__(self):
        self.ref_count = 1
        self.vtbl = IDropSourceVtbl(
            QueryInterface=QI_PROTO(self._QueryInterface),
            AddRef=ADDREF_PROTO(self._AddRef),
            Release=RELEASE_PROTO(self._Release),
            QueryContinueDrag=QUERYCONTINUE_PROTO(self._QueryContinueDrag),
            GiveFeedback=GIVEFEEDBACK_PROTO(self._GiveFeedback)
        )
        self.impl = IDropSourceImpl(lpVtbl=ctypes.pointer(self.vtbl))

    @property
    def ptr(self):
        return ctypes.cast(ctypes.pointer(self.impl), wintypes.LPVOID)

    def _QueryInterface(self, this, riid_ptr, ppv_ptr):
        if not riid_ptr or not ppv_ptr:
            return E_INVALIDARG
        riid = riid_ptr.contents.to_bytes()
        if riid in (IID_IUnknown.to_bytes(), IID_IDropSource.to_bytes()):
            ppv_ptr[0] = this
            self._AddRef(this)
            return S_OK
        ppv_ptr[0] = None
        return E_NOINTERFACE

    def _AddRef(self, this):
        self.ref_count += 1
        return self.ref_count

    def _Release(self, this):
        self.ref_count -= 1
        return self.ref_count

    def _QueryContinueDrag(self, this, fEscapePressed, grfKeyState):
        if fEscapePressed:
            return DRAGDROP_S_CANCEL
        # Si se soltó el botón principal del mouse, ejecutar Drop
        if not (grfKeyState & (MK_LBUTTON | MK_RBUTTON)):
            return DRAGDROP_S_DROP
        return S_OK

    def _GiveFeedback(self, this, dwEffect):
        # Usar cursores nativos estándar de Windows
        return DRAGDROP_S_USEDEFAULTCURSORS


# ─── Objeto de Datos para Arrastrar (IDataObject) ──────────────────────────────
class DataObject:
    def __init__(self, paths, preferred_effect=DROPEFFECT_MOVE):
        self.paths = [os.path.abspath(p) for p in paths if p and os.path.exists(p)]
        self.preferred_effect = preferred_effect
        self.performed_effect = DROPEFFECT_NONE
        self.paste_succeeded = False
        self.ref_count = 1
        self._active_enums = []

        self.supported_formats = [CF_HDROP, CF_PREFERREDDROPEFFECT, CF_UNICODETEXT]

        self.vtbl = IDataObjectVtbl(
            QueryInterface=QI_PROTO(self._QueryInterface),
            AddRef=ADDREF_PROTO(self._AddRef),
            Release=RELEASE_PROTO(self._Release),
            GetData=GETDATA_PROTO(self._GetData),
            GetDataHere=GETDATAHERE_PROTO(self._GetDataHere),
            QueryGetData=QUERYGETDATA_PROTO(self._QueryGetData),
            GetCanonicalFormatEtc=GETCANONICAL_PROTO(self._GetCanonicalFormatEtc),
            SetData=SETDATA_PROTO(self._SetData),
            EnumFormatEtc=ENUMFORMATETC_PROTO(self._EnumFormatEtc),
            DAdvise=DADVISE_PROTO(self._DAdvise),
            DUnadvise=DUNADVISE_PROTO(self._DUnadvise),
            EnumDAdvise=ENUMDADVISE_PROTO(self._EnumDAdvise)
        )
        self.impl = IDataObjectImpl(lpVtbl=ctypes.pointer(self.vtbl))

    @property
    def ptr(self):
        return ctypes.cast(ctypes.pointer(self.impl), wintypes.LPVOID)

    def _QueryInterface(self, this, riid_ptr, ppv_ptr):
        if not riid_ptr or not ppv_ptr:
            return E_INVALIDARG
        riid = riid_ptr.contents.to_bytes()
        if riid in (IID_IUnknown.to_bytes(), IID_IDataObject.to_bytes()):
            ppv_ptr[0] = this
            self._AddRef(this)
            return S_OK
        ppv_ptr[0] = None
        return E_NOINTERFACE

    def _AddRef(self, this):
        self.ref_count += 1
        return self.ref_count

    def _Release(self, this):
        self.ref_count -= 1
        return self.ref_count

    def _QueryGetData(self, this, pFormatetc_ptr):
        if not pFormatetc_ptr:
            return E_INVALIDARG
        cf = pFormatetc_ptr.contents.cfFormat
        tymed = pFormatetc_ptr.contents.tymed
        if cf in self.supported_formats and (tymed & TYMED_HGLOBAL):
            return S_OK
        return DV_E_FORMATETC

    def _GetData(self, this, pFormatetc_ptr, pMedium_ptr):
        if not pFormatetc_ptr or not pMedium_ptr:
            return E_INVALIDARG
        cf = pFormatetc_ptr.contents.cfFormat
        tymed = pFormatetc_ptr.contents.tymed

        if not (tymed & TYMED_HGLOBAL):
            return DV_E_FORMATETC

        if cf == CF_HDROP:
            df = DROPFILES()
            df.pFiles = ctypes.sizeof(DROPFILES)
            df.pt.x = 0
            df.pt.y = 0
            df.fNC = False
            df.fWide = True

            buf = bytearray(bytes(df))
            for p in self.paths:
                buf.extend(p.encode("utf-16le") + b"\x00\x00")
            buf.extend(b"\x00\x00") # Doble terminador nulo

            hMem = kernel32.GlobalAlloc(GHND, len(buf))
            pMem = kernel32.GlobalLock(hMem)
            ctypes.memmove(pMem, bytes(buf), len(buf))
            kernel32.GlobalUnlock(hMem)

            pMedium_ptr.contents.tymed = TYMED_HGLOBAL
            pMedium_ptr.contents.hGlobal = hMem
            pMedium_ptr.contents.pUnkForRelease = None
            return S_OK

        elif cf == CF_PREFERREDDROPEFFECT:
            val = wintypes.DWORD(self.preferred_effect)
            hMem = kernel32.GlobalAlloc(GHND, ctypes.sizeof(val))
            pMem = kernel32.GlobalLock(hMem)
            ctypes.memmove(pMem, ctypes.byref(val), ctypes.sizeof(val))
            kernel32.GlobalUnlock(hMem)

            pMedium_ptr.contents.tymed = TYMED_HGLOBAL
            pMedium_ptr.contents.hGlobal = hMem
            pMedium_ptr.contents.pUnkForRelease = None
            return S_OK

        elif cf == CF_UNICODETEXT:
            text = "\r\n".join(self.paths) + "\x00"
            raw = text.encode("utf-16le")
            hMem = kernel32.GlobalAlloc(GHND, len(raw))
            pMem = kernel32.GlobalLock(hMem)
            ctypes.memmove(pMem, raw, len(raw))
            kernel32.GlobalUnlock(hMem)

            pMedium_ptr.contents.tymed = TYMED_HGLOBAL
            pMedium_ptr.contents.hGlobal = hMem
            pMedium_ptr.contents.pUnkForRelease = None
            return S_OK

        return DV_E_FORMATETC

    def _GetDataHere(self, this, pFormatetc_ptr, pMedium_ptr):
        return E_NOTIMPL

    def _GetCanonicalFormatEtc(self, this, pFormatetcIn, pFormatetcOut):
        return E_NOTIMPL

    def _SetData(self, this, pFormatetc_ptr, pMedium_ptr, fRelease):
        if not pFormatetc_ptr or not pMedium_ptr:
            return E_INVALIDARG
        cf = pFormatetc_ptr.contents.cfFormat
        if cf == CF_PERFORMEDDROPEFFECT and pMedium_ptr.contents.hGlobal:
            pMem = kernel32.GlobalLock(pMedium_ptr.contents.hGlobal)
            if pMem:
                effect = wintypes.DWORD.from_address(pMem).value
                self.performed_effect = effect
                kernel32.GlobalUnlock(pMedium_ptr.contents.hGlobal)
        elif cf == CF_PASTESUCCEEDED:
            self.paste_succeeded = True
        return S_OK

    def _EnumFormatEtc(self, this, dwDirection, ppenum_ptr):
        if not ppenum_ptr:
            return E_INVALIDARG
        if dwDirection == DATADIR_GET:
            enum_obj = EnumFormatEtc(self.supported_formats)
            self._active_enums.append(enum_obj)
            ppenum_ptr[0] = enum_obj.ptr
            return S_OK
        ppenum_ptr[0] = None
        return E_NOTIMPL

    def _DAdvise(self, this, pFormatetc, advf, pAdvSink, pdwConnection):
        return E_NOTIMPL

    def _DUnadvise(self, this, dwConnection):
        return E_NOTIMPL

    def _EnumDAdvise(self, this, ppenumAdvise):
        return E_NOTIMPL


def _unpack_point(pt_raw):
    """Desempaqueta coordenadas X, Y desde un POINTL de 64 bits empaquetado en c_uint64"""
    if isinstance(pt_raw, int):
        x = ctypes.c_long(pt_raw & 0xFFFFFFFF).value
        y = ctypes.c_long((pt_raw >> 32) & 0xFFFFFFFF).value
        return x, y
    elif hasattr(pt_raw, 'x') and hasattr(pt_raw, 'y'):
        return pt_raw.x, pt_raw.y
    return 0, 0


# ─── Receptor de Soltado (IDropTarget) ─────────────────────────────────────────
class DropTarget:
    """Implementa IDropTarget para widgets Tkinter (como ttk.Treeview)"""

    def __init__(self, widget, on_drag_over=None, on_drag_leave=None, on_drop=None):
        self.widget = widget
        self.on_drag_over = on_drag_over
        self.on_drag_leave = on_drag_leave
        self.on_drop = on_drop
        self.ref_count = 1
        self._cached_files = []

        self.vtbl = IDropTargetVtbl(
            QueryInterface=QI_PROTO(self._QueryInterface),
            AddRef=ADDREF_PROTO(self._AddRef),
            Release=RELEASE_PROTO(self._Release),
            DragEnter=DRAGENTER_PROTO(self._DragEnter),
            DragOver=DRAGOVER_PROTO(self._DragOver),
            DragLeave=DRAGLEAVE_PROTO(self._DragLeave),
            Drop=DROP_PROTO(self._Drop)
        )
        self.impl = IDropTargetImpl(lpVtbl=ctypes.pointer(self.vtbl))

    @property
    def ptr(self):
        return ctypes.cast(ctypes.pointer(self.impl), wintypes.LPVOID)

    def _QueryInterface(self, this, riid_ptr, ppv_ptr):
        if not riid_ptr or not ppv_ptr:
            return E_INVALIDARG
        riid = riid_ptr.contents.to_bytes()
        if riid in (IID_IUnknown.to_bytes(), IID_IDropTarget.to_bytes()):
            ppv_ptr[0] = this
            self._AddRef(this)
            return S_OK
        ppv_ptr[0] = None
        return E_NOINTERFACE

    def _AddRef(self, this):
        self.ref_count += 1
        return self.ref_count

    def _Release(self, this):
        self.ref_count -= 1
        return self.ref_count

    def _DragEnter(self, this, pDataObj, grfKeyState, pt_raw, pdwEffect):
        try:
            self._cached_files = extract_hdrop_files(pDataObj)
            if self._cached_files:
                if pdwEffect:
                    pdwEffect[0] = DROPEFFECT_MOVE | DROPEFFECT_COPY
            else:
                if pdwEffect:
                    pdwEffect[0] = DROPEFFECT_NONE
        except Exception as e:
            print(f"[OleDragDrop] Error en DragEnter: {e}")
            if pdwEffect:
                try:
                    pdwEffect[0] = DROPEFFECT_NONE
                except Exception:
                    pass
        return S_OK

    def _DragOver(self, this, grfKeyState, pt_raw, pdwEffect):
        try:
            x, y = _unpack_point(pt_raw)
            # Convertir coordenadas de pantalla a relativas del widget
            wx = self.widget.winfo_rootx()
            wy = self.widget.winfo_rooty()
            local_x = x - wx
            local_y = y - wy

            effect = DROPEFFECT_MOVE | DROPEFFECT_COPY
            if self.on_drag_over:
                res = self.on_drag_over(local_x, local_y, grfKeyState)
                if res is not None:
                    effect = res

            if pdwEffect:
                pdwEffect[0] = effect
        except Exception:
            if pdwEffect:
                try:
                    pdwEffect[0] = DROPEFFECT_MOVE | DROPEFFECT_COPY
                except Exception:
                    pass
        return S_OK

    def _DragLeave(self, this):
        try:
            self._cached_files = []
            if self.on_drag_leave:
                self.on_drag_leave()
        except Exception:
            pass
        return S_OK

    def _Drop(self, this, pDataObj, grfKeyState, pt_raw, pdwEffect):
        try:
            files = self._cached_files or extract_hdrop_files(pDataObj)
            self._cached_files = []

            x, y = _unpack_point(pt_raw)
            wx = self.widget.winfo_rootx()
            wy = self.widget.winfo_rooty()
            local_x = x - wx
            local_y = y - wy

            effect = DROPEFFECT_NONE
            if self.on_drop and files:
                res = self.on_drop(local_x, local_y, files, grfKeyState)
                if res is not None:
                    effect = res
                else:
                    effect = DROPEFFECT_MOVE

            if pdwEffect:
                pdwEffect[0] = effect
        except Exception as e:
            print(f"[OleDragDrop] Error en Drop: {e}")
            if pdwEffect:
                try:
                    pdwEffect[0] = DROPEFFECT_NONE
                except Exception:
                    pass
        return S_OK


# ─── Funciones Utilitarias Públicas ────────────────────────────────────────────

def extract_hdrop_files(pDataObj):
    """Extrae la lista de rutas de archivos desde un puntero IDataObject vía CF_HDROP"""
    if not pDataObj:
        return []
    try:
        p_vtbl = ctypes.cast(pDataObj, ctypes.POINTER(ctypes.POINTER(wintypes.LPVOID)))
        vtbl = p_vtbl[0]
        GetData_func = GETDATA_PROTO(vtbl[3])

        fetc = FORMATETC(cfFormat=CF_HDROP, ptd=None, dwAspect=DVASPECT_CONTENT, lindex=-1, tymed=TYMED_HGLOBAL)
        stg = STGMEDIUM()
        hr = GetData_func(pDataObj, ctypes.byref(fetc), ctypes.byref(stg))
        if hr != S_OK or not stg.hGlobal:
            return []

        hDrop = stg.hGlobal
        count = shell32.DragQueryFileW(hDrop, 0xFFFFFFFF, None, 0)
        files = []
        for i in range(count):
            buf = ctypes.create_unicode_buffer(1024)
            shell32.DragQueryFileW(hDrop, i, buf, 1024)
            if buf.value:
                files.append(buf.value)

        # Liberar el medio de almacenamiento usando la función oficial de OLE (evita corrupción de heap y crashes)
        ole32.ReleaseStgMedium(ctypes.byref(stg))

        return files
    except Exception as e:
        print(f"[OleDragDrop] Error extrayendo HDROP: {e}")
        return []


def do_drag_drop(paths, preferred_effect=DROPEFFECT_MOVE):
    """
    Inicia un bucle de arrastrar y soltar nativo de Windows (DoDragDrop).
    
    Args:
        paths: Lista de rutas absolutas de archivos o carpetas a arrastrar.
        preferred_effect: DROPEFFECT_MOVE (2) o DROPEFFECT_COPY (1).
        
    Returns:
        tuple: (hr, dwEffect, performed_effect)
    """
    valid_paths = [p for p in paths if p and os.path.exists(p)]
    if not valid_paths:
        return (S_FALSE, DROPEFFECT_NONE, DROPEFFECT_NONE)

    dob = DataObject(valid_paths, preferred_effect=preferred_effect)
    ds = DropSource()

    dwEffect = wintypes.DWORD(0)
    okEffects = DROPEFFECT_COPY | DROPEFFECT_MOVE | DROPEFFECT_LINK

    # Llamada síncrona al bucle modal de Windows
    hr = ole32.DoDragDrop(dob.ptr, ds.ptr, okEffects, ctypes.byref(dwEffect))

    performed = dob.performed_effect if dob.performed_effect != DROPEFFECT_NONE else dwEffect.value
    return (hr, dwEffect.value, performed)


def register_drop_target(widget, on_drag_over=None, on_drag_leave=None, on_drop=None):
    """
    Registra un widget de Tkinter como destino de soltado (IDropTarget).
    
    Returns:
        DropTarget o None si falla.
    """
    try:
        widget.update_idletasks()
        hwnd = widget.winfo_id()
        if not hwnd:
            return None

        target = DropTarget(widget, on_drag_over=on_drag_over, on_drag_leave=on_drag_leave, on_drop=on_drop)
        hr = ole32.RegisterDragDrop(hwnd, target.ptr)
        if hr == S_OK:
            # Guardar referencia en el widget para evitar recolección de basura
            widget._ole_drop_target = target
            return target
        else:
            print(f"[OleDragDrop] RegisterDragDrop falló: {hex(hr)}")
            return None
    except Exception as e:
        print(f"[OleDragDrop] Error registrando DropTarget: {e}")
        return None


def revoke_drop_target(widget):
    """Revoca el registro de DropTarget de un widget"""
    try:
        hwnd = getattr(widget, "winfo_id", lambda: None)()
        if hwnd:
            ole32.RevokeDragDrop(hwnd)
        if hasattr(widget, "_ole_drop_target"):
            del widget._ole_drop_target
    except Exception:
        pass

