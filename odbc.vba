## Connect to query

Sub ConnectAndQuery()
    Dim conn As ADODB.Connection
    Dim rs As ADODB.Recordset
    Dim strSQL As String
    Dim strConn As String

    ' Replace with your DSN, username, and password
    strConn = "ODBC;DSN=YourDSNName;UID=YourUsername;PWD=YourPassword"
    strSQL = "SELECT * FROM YourTableName"  ' Replace with your actual SQL query

    ' Initialize connection
    Set conn = New ADODB.Connection
    conn.Open strConn

    ' Execute query
    Set rs = New ADODB.Recordset
    rs.Open strSQL, conn

    ' *** Do something with the recordset (rs) ***
    ' Example: Output to an Excel sheet
    Worksheets("Sheet1").Range("A1").CopyFromRecordset rs

    ' Close connections
    rs.Close
    conn.Close

    Set rs = Nothing
    Set conn = Nothing
End Sub
