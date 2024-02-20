Function Cell2(cellRef As Range) As String
    Dim sheetName As String
    Dim cellAddress As String
    
    ' Get the sheet name
    sheetName = cellRef.Parent.Name
    
    ' Get the cell address
    cellAddress = cellRef.Address
    
    ' Combine sheet name and cell address
    Cell2 = sheetName & "!" & cellAddress
End Function
