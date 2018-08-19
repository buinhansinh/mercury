import { Injectable } from "@angular/core";
import { Group } from "./group.model";
import { HttpClient } from "@angular/common/http";
import { Observable, of } from "rxjs";

@Injectable()
export class GroupService {
  constructor(private httpService: HttpClient) {}
  public getGroups(): Observable<Group[]> {
    return of([
      {
        id: "1",
        name: "Group 1"
      },
      {
        id: "2",
        name: "Group 2"
      },
      {
        id: "3",
        name: "Group 3"
      },
      {
        id: "4",
        name: "Group 4"
      }
    ]);
  }
}
