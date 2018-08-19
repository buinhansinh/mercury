import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { Permission } from "./permission.model";

@Injectable()
export class PermissionService {
  public getPermissions(): Observable<Permission[]> {
    return of([
      {
        id: "1",
        name: "CONTACT_CREATE"
      },
      {
        id: "2",
        name: "CONTACT_DELETE"
      },
      {
        id: "3",
        name: "CONTACT_UPDATE"
      },
      {
        id: "4",
        name: "CONTACT_READ"
      }
    ]);
  }
}
