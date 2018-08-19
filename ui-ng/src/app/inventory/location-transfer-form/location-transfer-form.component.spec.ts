import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { LocationTransferFormComponent } from "./location-transfer-form.component";

describe("LocationTransferFormComponent", () => {
  let component: LocationTransferFormComponent;
  let fixture: ComponentFixture<LocationTransferFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [LocationTransferFormComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LocationTransferFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
