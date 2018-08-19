import { Injectable, Inject } from "@angular/core";
import { User, Group } from "./user.model";
import { USERS } from "./user.mock";
import { of, Observable } from "rxjs";
import { HttpClient } from "@angular/common/http";
import { clone } from "../app-common/util";

export class MockUserService {
  private USERS: User[] = USERS;

  constructor() {}

  getById(id: string): Observable<User> {
    const results: User[] = this.USERS.filter(user => user.id === id);
    return of(results.length > 0 ? clone(results[0]) : null);
  }

  exists(name: string): Observable<User> {
    const results: User[] = this.USERS.filter(user => user.name === name);
    return of(results.length > 0 ? clone(results[0]) : null);
  }

  getAll(): Observable<User[]> {
    return of(clone(this.USERS));
  }

  put(user: User): void {
    this.USERS.push(user);
  }

  delete(user: User): void {
    this.USERS = this.USERS.filter(u => u.id !== user.id);
  }
}

export class HttpUserService {
  constructor(private http: HttpClient) {}

  getById(id: string): Observable<User> {
    return this.http.get<User>(`api/admin/user/${id}`);
  }

  getAll(): Observable<User[]> {
    return this.http.get<User[]>(`api/admin/user/`);
  }

  put(user: User): Observable<User> {
    return this.http.put<User>(`api/admin/user/`, user);
  }

  delete(user: User): Observable<User> {
    return this.http.delete<User>(`api/admin/user/${user.id}`);
  }

  exists(name: string): Observable<boolean> {
    return this.http.get<boolean>(`api/admin/user/exists/${name}`);
  }
}

@Injectable()
export class UserService extends MockUserService {}
