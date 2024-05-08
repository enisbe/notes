Function ExtractDatePattern(workbookName As String, partbefore As String, partafter As String) As String
    

    Dim startPosition As Integer
    Dim endPosition As Integer
    Dim datePattern As String
    
    ' Find the start and end positions of the date pattern
    startPosition = InStr(workbookName, partbefore) + Len(partbefore)
    endPosition = InStr(workbookName, partafter)

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

Function WorkbookIsOpen(name As String) As Boolean
    On Error Resume Next
    WorkbookIsOpen = Not (Workbooks(name) Is Nothing)
    On Error GoTo 0
End Function
 
Function ExtractFullPath(formula As String) As String
    Dim startPosition As Integer
    Dim endPosition As Integer
    Dim fullPath As String
    
    ' Find the start and end positions of the full path
    startPosition = InStr(1, formula, "='") + 2 ' Start after the opening "='"
    endPosition = InStr(startPosition, formula, "]") ' Find the closing "]" of the workbook name

    ' Extract the full path using the Mid function
    If startPosition > 0 And endPosition > 0 Then
        fullPath = Mid(formula, startPosition, endPosition - startPosition + 1)
    Else
        fullPath = "Path Not Found"
    End If
    
    ExtractFullPath = Replace(Replace(fullPath, "[", ""), "]", "")
    
End Function





Sub UpdateWorkbookReferences2()
    On Error GoTo ErrorHandler
    Dim ws As Worksheet
    Set ws = ActiveSheet

    Dim lastRow As Long
    ' lastRow = ws.Cells(ws.Rows.Count, "D").End(xlUp).Row
    selected_rows = Selection.Rows.Count
    firstRow = Selection.Rows(1).row
    
    
    Dim i As Long
    Dim cellFormula As String, wbname As String, date_str As String
 
    
    Application.ScreenUpdating = False

    For i = firstRow To selected_rows + firstRow - 1
        ' Formula we are updating
        
        cellFormula = ws.Cells(i, "F").formula
        replaceWhat = ws.Cells(i, "B").Value
        replaceWith = ws.Cells(i, "D").Value
        fullPath = ExtractFullPath(cellFormula)
        fullPathNew = Replace(fullPath, replaceWhat, replaceWith)
        wbname = ExtractWorkbookName(cellFormula)
        wbnameNew = Replace(wbname, replaceWhat, replaceWith)
        
        Debug.Print "Workbook Name: " & wbname
 
        If Not WorkbookIsOpen(wbname) Then
            Set externalWb = Workbooks.Open(Filename:=fullPathNew, Password:="test")
            newFormula = Replace(cellFormula, replaceWhat, replaceWith)
            ws.Cells(i, "F").formula = newFormula
            externalWb.Close SaveChanges:=False
        End If

    Next i
    Application.ScreenUpdating = True
    Exit Sub

ErrorHandler:
    MsgBox "Error: " & Err.Description & " (Line: " & Erl & ")"
End Sub
