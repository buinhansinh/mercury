import { Component, OnInit } from "@angular/core";
import { Observable } from "rxjs";
import { User } from "../../db/user.model";
import { UserService } from "../../db/user.service";
import { MatDialog } from "@angular/material";
import { UserFormComponent } from "../user-form/user-form.component";

@Component({
  selector: "app-users",
  templateUrl: "./users.component.html",
  styleUrls: ["./users.component.css"]
})
export class UsersComponent implements OnInit {
  users$: Observable<User[]>;
  displayedColumns = ["name", "display_name", "toolbox"];
  constructor(private userSerice: UserService, private dialog: MatDialog) {}

  ngOnInit() {
    this.users$ = this.userSerice.getAll();
  }

  onOpenAddUserForm() {
    const dialogRef = this.dialog.open(UserFormComponent, {
      position: {
        top: "120px"
      },
      width: "400px"
    });
  }
}
