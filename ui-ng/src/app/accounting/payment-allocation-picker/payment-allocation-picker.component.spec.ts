import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { PaymentAllocationPickerComponent } from "./payment-allocation-picker.component";

describe("PaymentAllocationPickerComponent", () => {
  let component: PaymentAllocationPickerComponent;
  let fixture: ComponentFixture<PaymentAllocationPickerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PaymentAllocationPickerComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PaymentAllocationPickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
