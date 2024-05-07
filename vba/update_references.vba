 

Function ExtractDatePattern(workbookName As String) As String
    Dim startPosition As Integer
    Dim endPosition As Integer
    Dim datePattern As String
    
    ' Find the start and end positions of the date pattern
    startPosition = InStr(workbookName, "workbook") + Len("workbook")
    endPosition = InStr(workbookName, ".xlsx")

    ' Extract the date pattern using Mid function
    If startPosition > 0 And endPosition > 0 Then
        datePattern = Mid(workbookName, startPosition, endPosition - startPosition)
    Else
        datePattern = "Pattern Not Found"
    End If
    
    ExtractDatePattern = Trim(datePattern)
End Function

Function ExtractWorkbookName(formula As String) As String
    Dim start As Integer
    Dim finish As Integer
    
    start = InStr(formula, "[") + 1
    finish = InStr(formula, "]") - 1
    
    ExtractWorkbookName = Mid(formula, start, finish - start + 1)
End Function



Sub UpdateWorkbookReferences()
    On Error GoTo ErrorHandler
    Dim ws As Worksheet
    Set ws = ActiveSheet

    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, "D").End(xlUp).Row
    
    Dim i As Long
    Dim cellFormula As String, wbname As String, date_str As String
    
    For i = 1 To lastRow
        cellFormula = ws.Cells(i, "F").formula
        wbname = ExtractWorkbookName(cellFormula)
        Debug.Print "Workbook Name: " & wbname
        replace_dt = ExtractDatePattern(wbname)
        ' Debug.Print "Date String: " & date_str
        new_dt = ws.Cells(i, "D").Value
        newFormula = Replace(cellFormula, replace_dt, new_dt)
        ws.Cells(i, "F").formula = newFormula
        Debug.Print "Date String: " & new_dt
  
    Next i
    
    Exit Sub

ErrorHandler:
    MsgBox "Error: " & Err.Description & " (Line: " & Erl & ")"
End Sub
