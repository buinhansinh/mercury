import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { OfferPickerComponent } from "./offer-picker.component";

describe("OfferPickerComponent", () => {
  let component: OfferPickerComponent;
  let fixture: ComponentFixture<OfferPickerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [OfferPickerComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OfferPickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
