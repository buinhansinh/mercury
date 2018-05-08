import {
    NgModule
} from '@angular/core';
import {
    RouterModule,
    Routes
} from '@angular/router';
import {
    PageNotFoundComponent
} from './page-not-found/page-not-found.component';
import {
    LoginComponent
} from './login/login.component';
import {
    DashboardComponent
} from './dashboard/dashboard.component';

const routes: Routes = [{
        path: 'login',
        component: LoginComponent
    },
    // {
    //     path: 'admin',
    //     loadChildren: './admin/admin.module#AdminModule'
    // },
    // {
    //     path: 'sales',
    //     loadChildren: './sales/sales.module#SalesModule'
    // },
    {
        path: 'dashboard',
        component: DashboardComponent,
    },
    {
        path: '',
        redirectTo: '/dashboard',
        pathMatch: 'full',
    },
    {
        path: '**',
        component: PageNotFoundComponent
    }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {}
