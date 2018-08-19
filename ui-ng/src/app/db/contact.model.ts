export interface Contact {
  id: string;
  name: string;
  numbers: string[];
  addresses: string[];
  emails: string[];
  links: string[];
  notes: string;
}

export const EMPTY_CONTACT: Contact = {
  id: null,
  name: null,
  numbers: ["", ""],
  addresses: ["", ""],
  emails: [""],
  links: [""],
  notes: null
};
