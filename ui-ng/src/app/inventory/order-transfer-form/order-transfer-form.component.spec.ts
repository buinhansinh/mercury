import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { OrderTransferFormComponent } from "./order-transfer-form.component";

describe("OrderTransferFormComponent", () => {
  let component: OrderTransferFormComponent;
  let fixture: ComponentFixture<OrderTransferFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [OrderTransferFormComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OrderTransferFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
