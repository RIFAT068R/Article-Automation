/**
 * @OnlyCurrentDoc
 * ZenithPress AI v2 - Google Sheets Database Web App Core
 * 
 * Instructions:
 * 1. Open your Google Sheet (create a new blank sheet if you don't have one).
 * 2. Click "Extensions" -> "Apps Script" in the top menu.
 * 3. Delete any code in the editor and paste this entire script.
 * 4. Click the Save icon (floppy disk).
 * 5. Click "Deploy" -> "New Deployment" (top right).
 * 6. Click the gear icon (Select type) -> Select "Web app".
 * 7. Configure:
 *    - Description: ZenithPress DB API
 *    - Execute as: "Me (your email)"
 *    - Who has access: "Anyone" (This is crucial so our backend script can call it without OAuth flows).
 * 8. Click "Deploy". Authorize permissions if Google asks.
 * 9. Copy the generated "Web app URL" and save it! You will use this in your backend config.
 */

// Global Sheet initialization and configuration
var SHEET_NAME = "Sheet1";

function setupHeaders(sheet) {
  var headers = ["Date", "Niche", "Topic", "Brief", "Cover Image Link", "Article", "Status"];
  var currentHeaders = sheet.getRange(1, 1, 1, headers.length).getValues()[0];
  
  var needsSetup = false;
  for (var i = 0; i < headers.length; i++) {
    if (currentHeaders[i] !== headers[i]) {
      needsSetup = true;
      break;
    }
  }
  
  if (needsSetup) {
    // Write headers and style them beautifully
    sheet.getRange(1, 1, 1, headers.length)
         .setValues([headers])
         .setFontWeight("bold")
         .setBackground("#1e293b")
         .setFontColor("#f8fafc")
         .setHorizontalAlignment("center");
         
    // Auto-fit column widths
    for (var col = 1; col <= headers.length; col++) {
      sheet.autoResizeColumn(col);
    }
    
    // Create an example niche column on a separate sheet tab or starting from row 2
    // If sheet is completely empty, let's write some default niches
    if (sheet.getLastRow() === 1) {
      sheet.appendRow([new Date(), "Artificial Intelligence", "Example AI Article Title", "An interesting brief summary of the AI article.", "https://picsum.photos/800/600", "# Welcome to ZenithPress AI\nThis is your first article draft.", "Draft"]);
    }
  }
}

function getActiveSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  setupHeaders(sheet);
  return sheet;
}

// 1. GET Request Handler
function doGet(e) {
  try {
    var sheet = getActiveSheet();
    var action = e.parameter.action || "get_articles";
    
    if (action === "get_niches") {
      // Fetch user specified target niches from the sheet
      // By default, we will look at column 2 (Niches) and extract unique, active niche tags
      var lastRow = sheet.getLastRow();
      if (lastRow < 2) {
        return createJsonResponse({ status: "success", niches: ["Tech", "Artificial Intelligence"] });
      }
      
      var values = sheet.getRange(2, 2, lastRow - 1, 1).getValues();
      var nichesSet = {};
      
      for (var i = 0; i < values.length; i++) {
        var val = values[i][0];
        if (val && typeof val === "string" && val.trim() !== "") {
          nichesSet[val.trim()] = true;
        }
      }
      
      var nichesList = Object.keys(nichesSet);
      if (nichesList.length === 0) {
        nichesList = ["Tech", "Artificial Intelligence"]; // Safe default fallbacks
      }
      
      return createJsonResponse({ status: "success", niches: nichesList });
    }
    
    if (action === "get_articles") {
      var lastRow = sheet.getLastRow();
      if (lastRow < 2) {
        return createJsonResponse({ status: "success", articles: [] });
      }
      
      var data = sheet.getRange(2, 1, lastRow - 1, 7).getValues();
      var articles = [];
      
      for (var i = 0; i < data.length; i++) {
        var row = data[i];
        articles.push({
          id: i + 1,
          date: row[0],
          niche: row[1],
          topic: row[2],
          brief: row[3],
          coverImageLink: row[4],
          article: row[5],
          status: row[6]
        });
      }
      
      // Return articles reversed so newest appear first
      articles.reverse();
      return createJsonResponse({ status: "success", articles: articles });
    }
    
    return createJsonResponse({ status: "error", message: "Unknown get action requested." });
    
  } catch (error) {
    return createJsonResponse({ status: "error", message: error.toString() });
  }
}

// 2. POST Request Handler
function doPost(e) {
  try {
    var sheet = getActiveSheet();
    var postData;
    
    if (e.postData && e.postData.contents) {
      postData = JSON.parse(e.postData.contents);
    } else {
      return createJsonResponse({ status: "error", message: "Missing POST request body content." });
    }
    
    var action = postData.action || "add_article";
    
    if (action === "add_article") {
      var date = postData.date ? new Date(postData.date) : new Date();
      var niche = postData.niche || "General Tech";
      var topic = postData.topic || "Untitled Post";
      var brief = postData.brief || "";
      var coverImageLink = postData.cover_image_link || "";
      var article = postData.article || "";
      var status = postData.status || "Published";
      
      // Append row to active sheet
      sheet.appendRow([date, niche, topic, brief, coverImageLink, article, status]);
      
      return createJsonResponse({ 
        status: "success", 
        message: "Article added successfully!",
        topic: topic 
      });
    }
    
    return createJsonResponse({ status: "error", message: "Unknown post action requested." });
    
  } catch (error) {
    return createJsonResponse({ status: "error", message: error.toString() });
  }
}

// Helper: Wrap data into clean JSON response format with correct CORS headers
function createJsonResponse(data) {
  var output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
