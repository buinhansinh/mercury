import { Component, OnInit } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { Permission } from "../../db/permission.model";
import { PermissionService } from "../../db/permission.service";
import { Observable } from "rxjs";

@Component({
  selector: "app-group-modify",
  templateUrl: "./group-modify.component.html",
  styleUrls: ["./group-modify.component.css"]
})
export class GroupModifyComponent implements OnInit {
  groupForm: FormGroup;
  permissionForm: FormGroup;
  permissions$: Observable<Permission[]>;
  permissionsForGroup: Permission[];
  constructor(
    private formBuilder: FormBuilder,
    private permissionSerivce: PermissionService
  ) {}

  ngOnInit() {
    this.groupForm = this.formBuilder.group({
      groupName: [null, Validators.required]
    });
    this.permissionForm = this.formBuilder.group({});
    this.permissions$ = this.permissionSerivce.getPermissions();
    this.permissionSerivce
      .getPermissions()
      .subscribe((permissions: Permission[]) => {
        this.permissionsForGroup = permissions;
      });
  }
}
