import { Contact } from "./contact.model";

export enum DocumentType {
  // sales
  SALE = 0,
  PURCHASE = 1,

  // inventory
  RELEASE = 2,
  RECEIPT = 3,
  TRANSFER = 4,
  ADJUSTMENT = 5,

  // accounting
  PAYMENT = 6,
  DISBURSEMENT = 7,
  EXPENSE = 8
}

export interface Document {
  id: string;
  contact: Contact;
  type: DocumentType;
  status: number;
  date: Date;
  ref_no: string;
  content: any;
}
