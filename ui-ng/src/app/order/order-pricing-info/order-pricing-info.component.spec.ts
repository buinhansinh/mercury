import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { OrderPricingInfoComponent } from "./order-pricing-info.component";

describe("OrderPricingInfoComponent", () => {
  let component: OrderPricingInfoComponent;
  let fixture: ComponentFixture<OrderPricingInfoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [OrderPricingInfoComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OrderPricingInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
