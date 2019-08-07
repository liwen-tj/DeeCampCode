import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import { LocaleProvider } from 'antd';
import zh_CN from 'antd/lib/locale-provider/zh_CN';
import 'moment/locale/zh-cn';
import './index.css';
import App from './App';
import Yin from './Yin';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
    <LocaleProvider locale={zh_CN}>
        <BrowserRouter>
            <Switch>
                <Route path='/' exact component={App} />
                <Route path='/schedule' exact component={Yin} />
            </Switch>
        </BrowserRouter>
    </LocaleProvider>
    , document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
