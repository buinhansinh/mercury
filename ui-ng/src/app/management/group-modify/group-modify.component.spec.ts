import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { GroupModifyComponent } from "./group-modify.component";

describe("GroupModifyComponent", () => {
  let component: GroupModifyComponent;
  let fixture: ComponentFixture<GroupModifyComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [GroupModifyComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GroupModifyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
