import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { LocationAdjustmentFormComponent } from "./location-adjustment-form.component";

describe("LocationAdjustmentFormComponent", () => {
  let component: LocationAdjustmentFormComponent;
  let fixture: ComponentFixture<LocationAdjustmentFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [LocationAdjustmentFormComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LocationAdjustmentFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
