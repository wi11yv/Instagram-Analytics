function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Drive Tools")
    .addItem("Import Files from Folder", "selectFolderAndImportFiles")
    .addToUi();
}

function selectFolderAndImportFiles() {
  const ui = SpreadsheetApp.getUi();
  const folderUrl = Browser.inputBox("Paste the Google Drive Folder URL:", Browser.Buttons.OK_CANCEL);

  if (folderUrl === "cancel" || folderUrl.trim() === "") {
    ui.alert("Operation canceled.");
    return;
  }

  const folderId = extractFolderId(folderUrl);
  if (!folderId) {
    ui.alert("Invalid folder URL. Please try again.");
    return;
  }

  importFilesToSheet(folderId);
}

function extractFolderId(url) {
  const match = url.match(/[-\w]{25,}/);
  return match ? match[0] : null;
}

function importFilesToSheet(folderId) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startCell = sheet.getActiveCell();
  let startRow = startCell.getRow();
  const startCol = startCell.getColumn();

  try {
    const folder = DriveApp.getFolderById(folderId);
    const filesWithFolders = getAllFilesRecursive(folder);

    // Sort files alphabetically
    filesWithFolders.sort((a, b) =>
      a.file.getName().toLowerCase().localeCompare(b.file.getName().toLowerCase())
    );

    // Header
    sheet.getRange(startRow, startCol, 1, 5).setValues([["Thumbnail", "File Name", "Description", "File Size", "Folder"]]);
    startRow++;

    filesWithFolders.forEach(({ file, folder }) => {
      const fileId = file.getId();
      const fileName = file.getName();
      const fileUrl = file.getUrl();
      const fileDescription = file.getDescription() || "";
      const fileSizeBytes = file.getSize();
      const fileSize =
        fileSizeBytes > 1024 * 1024
          ? (fileSizeBytes / (1024 * 1024)).toFixed(2) + " MB"
          : (fileSizeBytes / 1024).toFixed(2) + " KB";

      const thumbnailUrl = `https://drive.google.com/thumbnail?id=${fileId}`;
      const thumbnailFormula = `=HYPERLINK("${fileUrl}", IMAGE("${thumbnailUrl}", 1))`;
      sheet.getRange(startRow, startCol).setFormula(thumbnailFormula);

      const nameCell = sheet.getRange(startRow, startCol + 1);
      const richTextName = SpreadsheetApp.newRichTextValue()
        .setText(fileName)
        .setLinkUrl(fileUrl)
        .build();
      nameCell.setRichTextValue(richTextName);

      sheet.getRange(startRow, startCol + 2).setValue(fileDescription);
      sheet.getRange(startRow, startCol + 3).setValue(fileSize);

      const folderCell = sheet.getRange(startRow, startCol + 4);
      const richTextFolder = SpreadsheetApp.newRichTextValue()
        .setText(folder.getName())
        .setLinkUrl(folder.getUrl())
        .build();
      folderCell.setRichTextValue(richTextFolder);

      sheet.getRange(startRow, startCol, 1, 5).setWrap(true);
      startRow++;
    });

    SpreadsheetApp.getUi().alert("All files with clickable image previews and folder links imported successfully!");
  } catch (e) {
    SpreadsheetApp.getUi().alert("Error: " + e.message);
    Logger.log(e);
  }
}

function getAllFilesRecursive(folder) {
  let results = [];

  const fileIterator = folder.getFiles();
  while (fileIterator.hasNext()) {
    results.push({ file: fileIterator.next(), folder });
  }

  const subFolderIterator = folder.getFolders();
  while (subFolderIterator.hasNext()) {
    const subFolder = subFolderIterator.next();
    results = results.concat(getAllFilesRecursive(subFolder));
  }

  return results;
}
