Option Explicit

' BusquedaCarpetas - Manejador de protocolo busqueda://
' V7.3 - Deteccion automatica de OneDrive local

Dim url, path, originalPath
Dim shell, fso, wsh

If WScript.Arguments.Count = 0 Then WScript.Quit

url = WScript.Arguments(0)

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("Shell.Application")
Set wsh = CreateObject("WScript.Shell")

' ============================================================
' MODO DETECCION: busqueda://detect-onedrive?token=...&server=...
' El navegador llama esto para detectar las carpetas OneDrive
' del equipo cliente y reportarlas de vuelta al servidor.
' ============================================================
If InStr(LCase(url), "detect-onedrive") > 0 Then
    Dim token, serverUrl, odPaths, jsonBody, http
    Dim userProfileDet, mainFolder, subFolderDet

    ' --- Extraer token ---
    token = ""
    Dim tPos : tPos = InStr(LCase(url), "token=")
    If tPos > 0 Then
        token = Mid(url, tPos + 6)
        Dim tAmp : tAmp = InStr(token, "&")
        If tAmp > 0 Then token = Left(token, tAmp - 1)
    End If

    ' --- Extraer y decodificar URL del servidor ---
    serverUrl = ""
    Dim sPos : sPos = InStr(url, "server=")
    If sPos > 0 Then
        serverUrl = Mid(url, sPos + 7)
        serverUrl = Replace(serverUrl, "%3A", ":")
        serverUrl = Replace(serverUrl, "%3a", ":")
        serverUrl = Replace(serverUrl, "%2F", "/")
        serverUrl = Replace(serverUrl, "%2f", "/")
    End If

    ' --- Detectar carpetas OneDrive en %USERPROFILE% ---
    userProfileDet = wsh.ExpandEnvironmentStrings("%USERPROFILE%")
    odPaths = ""
    Set mainFolder = fso.GetFolder(userProfileDet)
    For Each subFolderDet In mainFolder.SubFolders
        If InStr(LCase(subFolderDet.Name), "onedrive") > 0 Then
            If odPaths <> "" Then odPaths = odPaths & Chr(1)
            odPaths = odPaths & subFolderDet.Path
        End If
    Next

    ' --- Enviar rutas al servidor via POST JSON ---
    If token <> "" And serverUrl <> "" And odPaths <> "" Then
        Dim pathArr : pathArr = Split(odPaths, Chr(1))
        Dim i
        jsonBody = "{""token"":""" & token & """,""paths"":["
        For i = 0 To UBound(pathArr)
            Dim escaped : escaped = Replace(pathArr(i), "\", "\\")
            If i > 0 Then jsonBody = jsonBody & ","
            jsonBody = jsonBody & """" & escaped & """"
        Next
        jsonBody = jsonBody & "]}"

        On Error Resume Next
        Set http = CreateObject("MSXML2.XMLHTTP")
        http.Open "POST", serverUrl & "/api/report-onedrive", False
        http.setRequestHeader "Content-Type", "application/json"
        http.Send jsonBody
        On Error GoTo 0
    End If

    WScript.Quit
End If

' ============================================================
' MODO NORMAL: abrir archivo o carpeta
' ============================================================

' Extraer el path de la URL de forma robusta
Dim pos
pos = InStr(LCase(url), "path=")
If pos > 0 Then
    originalPath = Mid(url, pos + 5)
Else
    ' Fallback si no encuentra path=
    originalPath = url
    originalPath = Replace(originalPath, "busqueda://open", "")
    originalPath = Replace(originalPath, "busqueda://folder", "")
    originalPath = Replace(originalPath, "/?path=", "")
    originalPath = Replace(originalPath, "?path=", "")
    originalPath = Replace(originalPath, ":", "")
End If

' Decodificacion de caracteres URL
path = originalPath
path = Replace(path, "%3A", ":")
path = Replace(path, "%5C", "\")
path = Replace(path, "%2F", "\")
path = Replace(path, "%20", " ")
path = Replace(path, "%28", "(")
path = Replace(path, "%29", ")")
path = Replace(path, "%2B", "+")
path = Replace(path, "%2C", ",")
path = Replace(path, "/", "\")

' UTF-8 Decoding para caracteres en espanol
path = Replace(path, "%C3%B3", Chr(243))
path = Replace(path, "%C3%93", Chr(211))
path = Replace(path, "%C3%B1", Chr(241))
path = Replace(path, "%C3%91", Chr(209))
path = Replace(path, "%C3%A1", Chr(225))
path = Replace(path, "%C3%81", Chr(193))
path = Replace(path, "%C3%A9", Chr(233))
path = Replace(path, "%C3%89", Chr(201))
path = Replace(path, "%C3%AD", Chr(237))
path = Replace(path, "%C3%8D", Chr(205))
path = Replace(path, "%C3%BA", Chr(250))
path = Replace(path, "%C3%9A", Chr(218))

' --- LOGICA DE PORTABILIDAD DE ONEDRIVE ---
' Si el path contiene "OneDrive", intentamos ajustarlo al usuario local
If InStr(LCase(path), "onedrive") > 0 Then
    Dim userProfile, parts, ii, newPath, found
    userProfile = wsh.ExpandEnvironmentStrings("%USERPROFILE%")

    found = False
    Dim folder, subFolder
    Set folder = fso.GetFolder(userProfile)
    For Each subFolder In folder.SubFolders
        If InStr(LCase(subFolder.Name), "onedrive") = 1 Then
            parts = Split(path, "\")
            For ii = 0 To UBound(parts)
                If InStr(LCase(parts(ii)), "onedrive") > 0 Then
                    newPath = subFolder.Path
                    Dim jj
                    For jj = ii + 1 To UBound(parts)
                        newPath = newPath & "\" & parts(jj)
                    Next
                    If fso.FileExists(newPath) Or fso.FolderExists(newPath) Then
                        path = newPath
                        found = True
                        Exit For
                    End If
                End If
            Next
        End If
        If found Then Exit For
    Next
End If

' --- EJECUCION ---
If InStr(url, "busqueda://folder") > 0 Then
    ' Modo carpeta
    If fso.FolderExists(path) Then
        shell.Open path
    ElseIf fso.FileExists(path) Then
        wsh.Run "explorer.exe /select,""" & path & """", 1, False
    Else
        MsgBox "No se pudo encontrar la carpeta o el archivo:" & vbCrLf & path, 48, "BusquedaCarpetas"
    End If
Else
    ' Modo archivo
    If fso.FileExists(path) Or fso.FolderExists(path) Then
        shell.Open path
    Else
        MsgBox "El archivo no existe en este equipo:" & vbCrLf & path & vbCrLf & vbCrLf & "Verifica que tengas sincronizada la carpeta de OneDrive.", 48, "BusquedaCarpetas"
    End If
End If
