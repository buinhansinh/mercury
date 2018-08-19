import { Component, OnInit } from "@angular/core";
import { FormGroup } from "@angular/forms";
import { ActivatedRoute, ParamMap } from "@angular/router";
import { User, Group, userBelongsTo } from "../../db/user.model";
import { UserService } from "../../db/user.service";

import { Observable } from "rxjs";
import { switchMap } from "rxjs/operators";

@Component({
  selector: "app-user",
  templateUrl: "./user.component.html",
  styleUrls: ["./user.component.css"]
})
export class UserComponent implements OnInit {
  public form: FormGroup;
  public user: User;
  public groups;
  public oldUsername: string;

  constructor(
    private route: ActivatedRoute,
    private userService: UserService
  ) {}

  public userBelongsTo = userBelongsTo;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get("id");
    const user$ = this.route.paramMap.pipe(
      switchMap((params: ParamMap, index: number) =>
        this.userService.getById(params.get("id"))
      )
    );
    user$.subscribe((user: User) => {
      this.user = user;
      this.oldUsername = user.name;
    });
    this.groups = [
      [Group.ADMIN, "Admin"],
      [Group.SALES, "Sales"],
      [Group.PURCHASING, "Purchasing"],
      [Group.INVENTORY, "Inventory"],
      [Group.ACCOUNTING, "Accounting"],
      [Group.MANAGEMENT, "Management"]
    ];
  }
}
