import { User, Group } from "./user.model";

export const USERS: User[] = [
  {
    id: "1",
    name: "sales",
    display_name: "Sales",
    groups: Group.SALES
  },
  {
    id: "2",
    name: "purchasing",
    display_name: "Purchasing",
    groups: Group.PURCHASING
  },
  {
    id: "3",
    name: "inventory",
    display_name: "Inventory",
    groups: Group.INVENTORY
  },
  {
    id: "4",
    name: "accounting",
    display_name: "Accounting",
    groups: Group.ACCOUNTING
  },
  {
    id: "5",
    name: "management",
    display_name: "Management",
    groups: Group.MANAGEMENT
  },
  {
    id: "6",
    name: "admin",
    display_name: "Admin",
    groups: Group.ADMIN
  }
];
