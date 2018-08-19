import { Component, OnInit, OnDestroy } from "@angular/core";
import { FormGroup, FormBuilder, FormArray } from "@angular/forms";
import { GroupService } from "../../db/group.service";
import { Observable } from "rxjs";
import { Group } from "../../db/group.model";
import { MatDialog } from "@angular/material";
import { GroupFormComponent } from "../group-form/group-form.component";

@Component({
  selector: "app-groups",
  templateUrl: "./groups.component.html",
  styleUrls: ["./groups.component.css"]
})
export class GroupsComponent implements OnInit {
  groups$: Observable<Group[]>;

  constructor(private groupSerice: GroupService, private dialog: MatDialog) {}

  ngOnInit() {
    this.groups$ = this.groupSerice.getGroups();
  }

  onOpenAddGroupForm() {
    const dialogRef = this.dialog.open(GroupFormComponent, {
      position: {
        top: "120px"
      },
      width: "400px"
    });
  }
}
