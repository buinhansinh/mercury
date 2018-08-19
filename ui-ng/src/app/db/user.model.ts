export enum Group {
  ADMIN = 1 << 0,
  SALES = 1 << 1,
  PURCHASING = 1 << 2,
  INVENTORY = 1 << 3,
  ACCOUNTING = 1 << 4,
  MANAGEMENT = 1 << 5
  // insert here
}

export interface User {
  id: string;
  name: string;
  display_name: string;
  groups: number;
}

export function userBelongsTo(user: User, group: Group): boolean {
  return (user.groups & group) === group;
}
