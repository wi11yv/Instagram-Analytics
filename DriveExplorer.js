function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Drive Tools")
    .addItem("Import Files from Folder or File", "selectDriveItemAndImport")
    .addToUi();
}

function selectDriveItemAndImport() {
  const ui = SpreadsheetApp.getUi();
  const inputUrl = Browser.inputBox("Paste the Google Drive Folder or File URL:", Browser.Buttons.OK_CANCEL);

  if (inputUrl === "cancel" || inputUrl.trim() === "") {
    ui.alert("Operation canceled.");
    return;
  }

  const id = extractDriveId(inputUrl);

  try {
    const file = DriveApp.getFileById(id);
    importSingleFileToSheet(file);
  } catch (e) {
    try {
      const folder = DriveApp.getFolderById(id);
      importFilesFromFolderToSheet(folder);
    } catch (err) {
      ui.alert("Invalid URL. Please provide a valid Google Drive folder or file URL.");
    }
  }
}

function extractDriveId(url) {
  const match = url.match(/[-\w]{25,}/);
  return match ? match[0] : null;
}

function importSingleFileToSheet(file) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startCell = sheet.getActiveCell();
  let startRow = startCell.getRow();
  const startCol = startCell.getColumn();

  const fileId = file.getId();
  const fileName = file.getName();
  const fileUrl = file.getUrl();
  const fileDescription = file.getDescription() || "";
  const fileSizeBytes = file.getSize();
  const fileSize = fileSizeBytes > 1024 * 1024
    ? (fileSizeBytes / (1024 * 1024)).toFixed(2) + " MB"
    : (fileSizeBytes / 1024).toFixed(2) + " KB";

  const thumbnailUrl = `https://drive.google.com/thumbnail?id=${fileId}`;
  sheet.getRange(startRow, startCol).setFormula(`=IMAGE("${thumbnailUrl}", 1)`);

  const nameCell = sheet.getRange(startRow, startCol + 1);
  const richText = SpreadsheetApp.newRichTextValue()
    .setText(fileName)
    .setLinkUrl(fileUrl)
    .build();
  nameCell.setRichTextValue(richText);

  sheet.getRange(startRow, startCol + 2).setValue(fileDescription);
  sheet.getRange(startRow, startCol + 3).setValue(fileSize);
  sheet.getRange(startRow, startCol + 4).setValue("Single File");
  sheet.getRange(startRow, startCol, 1, 5).setWrap(true);

  SpreadsheetApp.getUi().alert("File imported successfully!");
}

function importFilesFromFolderToSheet(folder) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startCell = sheet.getActiveCell();
  let startRow = startCell.getRow();
  const startCol = startCell.getColumn();

  const filesWithFolders = getAllFilesRecursive(folder, folder.getName());

  // Sort files alphabetically
  filesWithFolders.sort((a, b) =>
    a.file.getName().toLowerCase().localeCompare(b.file.getName().toLowerCase())
  );

  filesWithFolders.forEach(({ file, folderPath }) => {
    const fileId = file.getId();
    const fileName = file.getName();
    const fileUrl = file.getUrl();
    const fileDescription = file.getDescription() || "";
    const fileSizeBytes = file.getSize();
    const fileSize = fileSizeBytes > 1024 * 1024
      ? (fileSizeBytes / (1024 * 1024)).toFixed(2) + " MB"
      : (fileSizeBytes / 1024).toFixed(2) + " KB";

    const thumbnailUrl = `https://drive.google.com/thumbnail?id=${fileId}`;
    sheet.getRange(startRow, startCol).setFormula(`=IMAGE("${thumbnailUrl}", 1)`);

    const nameCell = sheet.getRange(startRow, startCol + 1);
    const richText = SpreadsheetApp.newRichTextValue()
      .setText(fileName)
      .setLinkUrl(fileUrl)
      .build();
    nameCell.setRichTextValue(richText);

    sheet.getRange(startRow, startCol + 2).setValue(fileDescription);
    sheet.getRange(startRow, startCol + 3).setValue(fileSize);
    sheet.getRange(startRow, startCol + 4).setValue(folderPath);
    sheet.getRange(startRow, startCol, 1, 5).setWrap(true);

    startRow++;
  });

  SpreadsheetApp.getUi().alert("All files imported successfully!");
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
