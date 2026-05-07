Option Explicit

' BusquedaCarpetas - Manejador de protocolo busqueda://
' V7.2 - Compatible con rutas de OneDrive locales de cada usuario

Dim url, path, originalPath
Dim shell, fso, wsh

If WScript.Arguments.Count = 0 Then WScript.Quit

url = WScript.Arguments(0)

' Extraer el path de la URL
originalPath = url
originalPath = Replace(originalPath, "busqueda://open?path=", "")
originalPath = Replace(originalPath, "busqueda://folder?path=", "")

' Decodificación manual de caracteres URL
path = originalPath
path = Replace(path, "%3A", ":")
path = Replace(path, "%5C", "\")
path = Replace(path, "%2F", "\")
path = Replace(path, "%20", " ")
path = Replace(path, "%28", "(")
path = Replace(path, "%29", ")")
path = Replace(path, "%C3%B3", "ó")
path = Replace(path, "%C3%B1", "ñ")
path = Replace(path, "%C3%A9", "é")
path = Replace(path, "%C3%A1", "á")
path = Replace(path, "%C3%AD", "í")
path = Replace(path, "%C3%BA", "ú")
path = Replace(path, "%2B", "+")
path = Replace(path, "%2C", ",")
path = Replace(path, "/", "\")

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("Shell.Application")
Set wsh = CreateObject("WScript.Shell")

' --- LOGICA DE PORTABILIDAD DE ONEDRIVE ---
' Si el path contiene "OneDrive", intentamos ajustarlo al usuario local
If InStr(LCase(path), "onedrive") > 0 Then
    Dim userProfile, localOneDrive, parts, i, newPath, found
    userProfile = wsh.ExpandEnvironmentStrings("%USERPROFILE%")
    
    ' Intentar encontrar la carpeta OneDrive local
    ' Buscamos en el perfil del usuario carpetas que empiecen por "OneDrive"
    found = False
    Dim folder, subFolder
    Set folder = fso.GetFolder(userProfile)
    For Each subFolder In folder.SubFolders
        If InStr(LCase(subFolder.Name), "onedrive") = 1 Then
            ' Encontramos un OneDrive local. Ahora intentamos reconstruir la ruta relativa
            ' El path original suele ser algo como C:\Users\Elkin\OneDrive - Empresa\Carpeta\...
            ' Queremos la parte despues de "OneDrive - Empresa"
            
            parts = Split(path, "\")
            For i = 0 To UBound(parts)
                If InStr(LCase(parts(i)), "onedrive") > 0 Then
                    ' Reconstruir desde aqui
                    newPath = subFolder.Path
                    Dim j
                    For j = i + 1 To UBound(parts)
                        newPath = newPath & "\" & parts(j)
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
