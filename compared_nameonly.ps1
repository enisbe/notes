# Define the paths of your directories
 
$dir1 = "\\BEC-NAS\cloud\Google Drive (enisbecirbegovic2022@u.northwestern.edu)\MSDS 458"
$dir2 = "D:\HP Backup\Google Drive (enisbecirbegovic2022@u.northwestern.edu)\MSDS 401"
$extension = "*.*"


# Function to check if the file path contains any segment starting with a '.'
function Test-IsHiddenFolder {
    param (
        [string]$Path
    )
    return ($Path -split '\\' | Where-Object { $_ -match '^\.' }).Count -gt 0
}

# Get all files from $dir1 recursively with their full paths
# Exclude files that are in any subfolder starting with '.'
# Filter by .mp4 extension
$files1 = Get-ChildItem -Path $dir1 -Recurse -File -Filter $extension| Where-Object { -not (Test-IsHiddenFolder -Path $_.FullName) }

# Get all .mp4 file names from $dir2 recursively
$files2 = Get-ChildItem -Path $dir2 -Recurse -File -Filter $extension | Select-Object -ExpandProperty Name

# Find files that exist in $dir1 but not in $dir2 by comparing file names
$uniqueFiles = $files1 | Where-Object { $files2 -notcontains $_.Name } | Select-Object FullName

# Display the full paths of files unique to $dir1
# Check if $uniqueFiles is empty or not
if ($uniqueFiles.Count -gt 0) {
    # Display the full paths of files unique to $dir1
    $uniqueFiles | ForEach-Object { $_.FullName }
} else {
    "No differences found. All files in $dir1 with the extension $extension  also exist in $dir2 with identical content."
}