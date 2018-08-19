import { Component, OnInit } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";

@Component({
  selector: "app-group-form",
  templateUrl: "./group-form.component.html",
  styleUrls: ["./group-form.component.css"]
})
export class GroupFormComponent implements OnInit {
  groupForm: FormGroup;
  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.groupForm = this.formBuilder.group({
      groupName: [null, Validators.required]
    });
  }

  onCreateGroup() {}
}
