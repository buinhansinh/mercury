/*
    Utility functions
*/

// create a deep copy of an object
export function clone(obj: any) {
  return JSON.parse(JSON.stringify(obj));
}

// python-like range() function
export function range(n: number) {
  const r = new Array(n);
  for (let i = 0; i < n; i++) {
    r[i] = i;
  }
  return r;
}

export function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.substr(1).toLowerCase();
}
