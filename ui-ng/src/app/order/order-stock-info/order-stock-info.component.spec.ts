import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { OrderStockInfoComponent } from "./order-stock-info.component";

describe("OrderStockInfoComponent", () => {
  let component: OrderStockInfoComponent;
  let fixture: ComponentFixture<OrderStockInfoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [OrderStockInfoComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OrderStockInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
