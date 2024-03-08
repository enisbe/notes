# Define the paths of your directories
$dir1 = "\\BEC-NAS\cloud\Google Drive (enisbecirbegovic2022@u.northwestern.edu)\MSDS 458"
$dir2 = "D:\HP Backup\Google Drive (enisbecirbegovic2022@u.northwestern.edu)\MSDS 401"
$exclude_folder = "Path\To\Exclude\Folder" # Specify the folder path to exclude
$extension = "*.*"

# Function to check if the file path contains any segment starting with a '.'
function Test-IsHiddenFolder {
    param (
        [string]$Path
    )
    return ($Path -split '\\' | Where-Object { $_ -match '^\.' }).Count -gt 0
}

# Function to check if the file path is under the excluded folder
function Test-IsExcludedFolder {
    param (
        [string]$FilePath,
        [string]$ExcludedFolderPath
    )
    return $FilePath.StartsWith($ExcludedFolderPath)
}

# Get all files from $dir1 recursively with their full paths
# Exclude files that are in any subfolder starting with '.' or in the excluded folder
$files1 = Get-ChildItem -Path $dir1 -Recurse -File -Filter $extension | Where-Object { -not (Test-IsHiddenFolder -Path $_.FullName) -and -not (Test-IsExcludedFolder -FilePath $_.FullName -ExcludedFolderPath $exclude_folder) }

# Get all file names from $dir2 recursively
$files2 = Get-ChildItem -Path $dir2 -Recurse -File -Filter $extension | Select-Object -ExpandProperty Name

# Find files that exist in $dir1 but not in $dir2 by comparing file names
$uniqueFiles = $files1 | Where-Object { $files2 -notcontains $_.Name }

# Determine the name for the new subdirectory
$dir2LastFolderName = Split-Path -Path $dir2 -Leaf
$newSubdirectory = Join-Path -Path (Split-Path -Path $dir2 -Parent) -ChildPath ("difference_" + $dir2LastFolderName)

# Check if $uniqueFiles is not empty
if ($uniqueFiles.Count -gt 0) {
    # Create the new subdirectory if it doesn't exist
    if (-not (Test-Path -Path $newSubdirectory)) {
        New-Item -Path $newSubdirectory -ItemType Directory
    }
    
    # Move each unique file to the new subdirectory, maintaining the folder structure
    $uniqueFiles | ForEach-Object {
        $relativePath = $_.FullName.Substring($dir1.Length)
        $destinationPath = Join-Path -Path $newSubdirectory -ChildPath $relativePath
        $destinationDir = Split-Path -Path $destinationPath -Parent
        if (-not (Test-Path -Path $destinationDir)) {
            New-Item -Path $destinationDir -ItemType Directory -Force
        }
        Move-Item -Path $_.FullName -Destination $destinationPath
    }
} else {
    "No differences found. All files in $dir1 with the extension $extension also exist in $dir2."
}
