Function Cell2(reference As Range) As String
    Dim fullPath As String
    Dim sheetAndCell As String
    Dim startPos As Integer
    
    ' Get the full path, sheet, and cell reference using the CELL function
    fullPath = Application.WorksheetFunction.Cell("filename", reference)
    
    ' Find the position of the closing bracket "]" which marks the end of the file path
    startPos = InStrRev(fullPath, "]")
    
    ' Extract everything after the closing bracket, which is the sheet and cell reference
    If startPos > 0 Then
        sheetAndCell = Mid(fullPath, startPos + 1)
    Else
        sheetAndCell = fullPath ' In case the reference is in the same sheet and CELL does not include file path
    End If
    
    ' Return the extracted sheet and cell reference
    Cell2 = sheetAndCell
End Function
