import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { RefundFormComponent } from "./refund-form.component";

describe("RefundFormComponent", () => {
  let component: RefundFormComponent;
  let fixture: ComponentFixture<RefundFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [RefundFormComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RefundFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
