// GTL TEST – Zone-wise Google Sheets JSONP endpoint.
// Replace SHEET_ID only if the master spreadsheet changes.
// Deploy: Web App / Execute as Me / Access per company IT policy.
const SHEET_ID="1oUJAlRY3zArl37uLcMrunD9pjPQUUX9bpJNZzcyxAFU";
function doGet(e){
  const cb=String(e.parameter.callback||"GTLReceiveZoneData");
  if(!/^[A-Za-z_$][\w$]*$/.test(cb))return ContentService.createTextOutput("Invalid callback");
  const ss=SpreadsheetApp.openById(SHEET_ID);
  const sh=ss.getSheetByName("Details")||ss.getSheets()[0];
  const values=sh.getDataRange().getValues();
  const idx=values.findIndex(r=>r.some(c=>String(c).trim().toUpperCase()==="BUILDING NAME"));
  if(idx<0)throw Error("BUILDING NAME header not found");
  const heads=values[idx].map(v=>String(v).trim().toUpperCase().replace(/\s+/g," "));
  const at=(row,key)=>row[heads.indexOf(key)]??"";
  const number=v=>Number(v)||0;
  const rows=values.slice(idx+1).filter(r=>at(r,"BUILDING NAME")&&at(r,"FLOOR LEVEL")).map(r=>({
    building:String(at(r,"BUILDING NAME")).trim().toUpperCase(),floor:String(at(r,"FLOOR LEVEL")).trim(),
    subLocation:String(at(r,"SUB LOCATION")),storeType:String(at(r,"STORE TYPE")),zone:String(at(r,"ZONE")),
    total:number(at(r,"TOTAT AREA")||at(r,"TOTAL AREA")),non:number(at(r,"NON SELLING")),
    rented:number(at(r,"RENTED")),used:number(at(r,"USING")),
    balance:Math.max(0,number(at(r,"BALANCE"))),cbm:number(at(r,"CBM"))
  }));
  return ContentService.createTextOutput(cb+"("+JSON.stringify({rows,refreshSeconds:120})+");").setMimeType(ContentService.MimeType.JAVASCRIPT);
}