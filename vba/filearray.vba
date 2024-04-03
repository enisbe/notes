=OFFSET(D4, 0, 0, COUNTA(D:D), 1)

Function ListCsvFilesArray(folderPath As String, Optional Transpose As Boolean = False) As Variant
    Dim fileNames() As String
    Dim fileName As String
    Dim i As Integer
    
    ' Ensure folder path ends with a backslash
    If Right(folderPath, 1) <> "\" Then
        folderPath = folderPath & "\"
    End If
    
    ' Initialize array size and counter
    ReDim fileNames(0)
    i = 0
    
    ' Start looking for .csv files in the specified folder
    fileName = Dir(folderPath & "*.csv")
    
    ' Loop until no more matching files are found
    Do While fileName <> ""
        ' Resize the array and add the file name
        ReDim Preserve fileNames(i)
        fileNames(i) = fileName
        i = i + 1
        fileName = Dir() ' Find next file
    Loop
    
    ' Check if any files were found
    If i = 0 Then
        ListCsvFilesArray = Array("No .csv files found.")
    Else
        If Transpose Then
            ' If Transpose is True, transpose the array
            ListCsvFilesArray = Application.Transpose(fileNames)
        Else
            ListCsvFilesArray = fileNames
        End If
    End If
End Function
