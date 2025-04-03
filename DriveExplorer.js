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
      const filesWithFolders = getAllFilesRecursive(folder, folder.getName());
  
      // Sort files alphabetically
      filesWithFolders.sort((a, b) =>
        a.file.getName().toLowerCase().localeCompare(b.file.getName().toLowerCase())
      );
  
      // Header (optional)
      sheet.getRange(startRow, startCol, 1, 5).setValues([["Thumbnail", "File Name", "Description", "File Size", "Folder"]]);
      startRow++;
  
      filesWithFolders.forEach(({ file, folderPath }) => {
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
  
      SpreadsheetApp.getUi().alert("All files with folder names imported successfully!");
    } catch (e) {
      SpreadsheetApp.getUi().alert("Error: " + e.message);
      Logger.log(e);
    }
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
  
