<#
.SYNOPSIS
This script compares files by content between two directories, focusing on any file or specific  files (extension="*.mp4". It identifies files that exist in the first directory but not in the second, 
regardless of their names or locations within the directories.

.DESCRIPTION
The script uses MD5 hashes to compare the content of .mp4 files in two specified directories. It filters out files in directories starting with a '.', considering these as hidden or system directories. 
The comparison is based on file content, allowing identification of files that are the same but may have different names or locations in the directory structure.

.PARAMETERS
- $dir1: The path to the source directory from which files will be compared.
- $dir2: The path to the target directory against which the source directory files will be compared.

.EXAMPLE
To use this script, modify the $dir1 and $dir2 variables to point to your source and target directories, respectively. Ensure PowerShell execution policies allow script execution. Run the script in a PowerShell session.

.NOTES
The script may take some time to execute, especially for large directories or over slow network connections, as it computes MD5 hashes for each file.
#>


# Define the paths of your directories
$dir1 = "\\BEC-NAS\cloud\Google Drive (enisbecirbegovic2022@u.northwestern.edu)\MSDS 498"
$dir2 = "D:\HP Backup\Google Drive (enisbecirbegovic2022@u.northwestern.edu)\MSDS 498"

$extension = "*.mkv"


# Function to check if the file path contains any segment starting with a '.'
function Test-IsHiddenFolder {
    param (
        [string]$Path
    )
    return ($Path -split '\\' | Where-Object { $_ -match '^\.' }).Count -gt 0
}

# Function to get the hash value of a file's content
function Get-FileHashValue {
    param (
        [string]$Path
    )
    try {
        return (Get-FileHash -Path $Path -Algorithm MD5).Hash
    } catch {
        return $null
    }
}

# Get all files from $dir1 recursively with their full paths
# Exclude files that are in any subfolder starting with '.'


# Filter by .mp4 extension and compute their hash values
$files1 = Get-ChildItem -Path $dir1 -Recurse -File -Filter $extension | Where-Object { -not (Test-IsHiddenFolder -Path $_.FullName) }
$files1Hashes = $files1 | ForEach-Object { @{ FullName = $_.FullName; Hash = (Get-FileHashValue -Path $_.FullName) } }

# Get all .mp4 files from $dir2 recursively and compute their hash values
$files2 = Get-ChildItem -Path $dir2 -Recurse -File -Filter $extension | Where-Object { -not (Test-IsHiddenFolder -Path $_.FullName) }
$files2Hashes = $files2 | ForEach-Object { @{ FullName = $_.FullName; Hash = (Get-FileHashValue -Path $_.FullName) } }

# Compare file hashes to find files in $dir1 that are not in $dir2
$uniqueFiles = $files1Hashes | Where-Object { $_.Hash -and ($files2Hashes.Hash -notcontains $_.Hash) } | Select-Object FullName

# Display the full paths of files unique to $dir1
# Check if $uniqueFiles is empty or not
if ($uniqueFiles.Count -gt 0) {
    # Display the full paths of files unique to $dir1
    $uniqueFiles | ForEach-Object { $_.FullName }
} else {
    "No differences found. All files in $dir1 with the extension $extension  also exist in $dir2 with identical content."
}