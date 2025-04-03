function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Drive Tools")
    .addItem("Import Files", "selectAndImport")
    .addToUi();
}

function selectAndImport() {
  const ui = SpreadsheetApp.getUi();
  const inputUrl = Browser.inputBox("Paste the Google Drive Folder or File URL:", Browser.Buttons.OK_CANCEL);

  if (inputUrl === "cancel" || inputUrl.trim() === "") {
    ui.alert("Operation canceled.");
    return;
  }

  const id = extractFolderId(inputUrl);
  if (!id) {
    ui.alert("Invalid URL. Please try again.");
    return;
  }

  try {
    const file = DriveApp.getFileById(id);
    importSingleFileToSheet(file);
  } catch (e) {
    try {
      const folder = DriveApp.getFolderById(id);
      importFilesToSheet(folder);
    } catch (err) {
      ui.alert("Unable to access file or folder: " + err.message);
    }
  }
}

function extractFolderId(url) {
  const match = url.match(/[-\w]{25,}/);
  return match ? match[0] : null;
}

function importFilesToSheet(folder) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startCell = sheet.getActiveCell();
  let startRow = startCell.getRow();
  const startCol = startCell.getColumn();

  const filesWithFolders = getAllFilesRecursive(folder, folder.getName());
  filesWithFolders.sort((a, b) => a.file.getName().toLowerCase().localeCompare(b.file.getName().toLowerCase()));

  filesWithFolders.forEach(({ file, folderPath }) => {
    writeFileRow(sheet, startRow++, startCol, file, folderPath);
  });

  SpreadsheetApp.getUi().alert("Files imported successfully!");
}

function importSingleFileToSheet(file) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startCell = sheet.getActiveCell();
  const startRow = startCell.getRow();
  const startCol = startCell.getColumn();
  writeFileRow(sheet, startRow, startCol, file, "Single File");
  SpreadsheetApp.getUi().alert("Single file imported successfully!");
}

function writeFileRow(sheet, row, col, file, folderPath) {
  const fileId = file.getId();
  const fileName = file.getName();
  const fileUrl = file.getUrl();
  const fileDescription = file.getDescription() || "";
  const fileSizeBytes = file.getSize();
  const fileSize = fileSizeBytes > 1024 * 1024
    ? (fileSizeBytes / (1024 * 1024)).toFixed(2) + " MB"
    : (fileSizeBytes / 1024).toFixed(2) + " KB";

  const thumbnailUrl = `https://drive.google.com/thumbnail?id=${fileId}`;
  sheet.getRange(row, col).setFormula(`=IMAGE(\"${thumbnailUrl}\", 1)`);

  const nameCell = sheet.getRange(row, col + 1);
  const richText = SpreadsheetApp.newRichTextValue()
    .setText(fileName)
    .setLinkUrl(fileUrl)
    .build();
  nameCell.setRichTextValue(richText);

  sheet.getRange(row, col + 2).setValue(fileDescription);
  sheet.getRange(row, col + 3).setValue(fileSize);
  sheet.getRange(row, col + 4).setValue(folderPath);
  sheet.getRange(row, col, 1, 5).setWrap(true);
}

function getAllFilesRecursive(folder, path) {
  let results = [];
  const fileIterator = folder.getFiles();
  while (fileIterator.hasNext()) {
    results.push({ file: fileIterator.next(), folderPath: path });
  }
  const subFolderIterator = folder.getFolders();
  while (subFolderIterator.hasNext()) {
    const subFolder = subFolderIterator.next();
    const subPath = `${path} / ${subFolder.getName()}`;
    results = results.concat(getAllFilesRecursive(subFolder, subPath));
  }
  return results;
}
