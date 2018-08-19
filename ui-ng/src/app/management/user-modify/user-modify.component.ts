import { Component, OnInit } from "@angular/core";
import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { Observable } from "rxjs";
import { Group } from "../../db/group.model";
import { GroupService } from "../../db/group.service";

@Component({
  selector: "app-user-modify",
  templateUrl: "./user-modify.component.html",
  styleUrls: ["./user-modify.component.css"]
})
export class UserModifyComponent implements OnInit {
  userForm: FormGroup;
  passwordForm: FormGroup;
  groups$: Observable<Group[]>;
  groupColumns = ["name", "toolbar"];
  constructor(
    private formBuilder: FormBuilder,
    private groupService: GroupService
  ) {}

  ngOnInit() {
    this.userForm = this.formBuilder.group({
      username: [null, Validators.required],
      fullname: [null, Validators.required]
    });
    this.passwordForm = this.formBuilder.group({
      password: [null, Validators.required],
      passwordVerify: [null, Validators.required]
    });
    this.groups$ = this.groupService.getGroups();
  }
}
