import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { PaymentAllocationComponent } from "./payment-allocation.component";

describe("PaymentAllocationComponent", () => {
  let component: PaymentAllocationComponent;
  let fixture: ComponentFixture<PaymentAllocationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PaymentAllocationComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PaymentAllocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
