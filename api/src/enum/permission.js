Enum = require("enum");
dict = require("./dict");

// CAUTION: Never delete enum values and never change their order!
// Database keys are dependent on their order and changing them will break consistency

const Permission = new Enum(dict([
  "CONTACT_VIEW",
  "CONTACT_MODIFY",
  "CONTACT_ARCHIVE",
  "CONTACT_MERGE",

  "OFFER_VIEW",
  "OFFER_MODIFY",
  "OFFER_ARCHIVE",
  "OFFER_MERGE",

  "LOCATION_VIEW",
  "LOCATION_MODIFY",
  "LOCATION_ARCHIVE",
  "LOCATION_MERGE",

  "SALES_VIEW",
  "SALES_MODIFY",
  "SALES_CANCEL",

  "PURCHASE_VIEW",
  "PURCHASE_MODIFY",
  "PURCHASE_CANCEL",

  "SALES_TRANSFER_VIEW",
  "SALES_TRANSFER_MODIFY",
  "SALES_TRANSFER_CANCEL",

  "PURCHASE_TRANSFER_VIEW",
  "PURCHASE_TRANSFER_MODIFY",
  "PURCHASE_TRANSFER_CANCEL",

  "LOCATION_TRANSFER_VIEW",
  "LOCATION_TRANSFER_MODIFY",
  "LOCATION_TRANSFER_CANCEL",

  "LOCATION_ADJUSTMENT_VIEW",
  "LOCATION_ADJUSTMENT_MODIFY",
  "LOCATION_ADJUSTMENT_CANCEL",

  "COLLECTION_VIEW",
  "COLLECTION_MODIFY",
  "COLLECTION_CANCEL",
  "COLLECTION_ALLOCATION",

  "DISBURSEMENT_VIEW",
  "DISBURSEMENT_MODIFY",
  "DISBURSEMENT_CANCEL",
  "DISBURSEMENT_ALLOCATION",

  "EXPENSE_VIEW",
  "EXPENSE_MODIFY",
  "EXPENSE_CANCEL"
]));

module.exports = Permission;
