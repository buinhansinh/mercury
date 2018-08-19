import { Component, OnInit } from "@angular/core";
import { UserService } from "../db/user.service";
import { User } from "../db/user.model";
import { Observable } from "rxjs";

@Component({
  selector: "app-admin",
  templateUrl: "./admin.component.html",
  styleUrls: ["./admin.component.css"]
})
export class AdminComponent implements OnInit {
  public users$: Observable<User[]>;

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.users$ = this.userService.getAll();
  }
}
