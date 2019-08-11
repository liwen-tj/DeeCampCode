import Jia from './Jia';
import React from 'react';
import EditableTable from './Csv2Table';
import './Yin.css';
import { Tabs, notification, Button } from 'antd';
import API from './utils/api.js';
import Headers from './utils/headers.js';
import { LineChart, Pie, LineChart2 } from './myChart';
import bar from './img/bar.jpeg';

const { TabPane } = Tabs;

function callback(key) {
    console.log(key);
}

class Yin extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            activeKey: '1',
            scheduleValue: '[]',
            chartData: '[]',
            envSetting: {startTime: '', endTime: ''},
        };
    };

    handleClick = () => {
        // localStorage.setItem("predict", EditableTable.dataSource);
        // console.log(EditableTable.dataSource);
        this.setState({ activeKey: '2' });
        notification.open({
            message: '提交成功！',
            description: '正在生成调度表',
            duration: 7
        });

        let setting_json = JSON.parse(localStorage.getItem("setting"));
        let predict_array = JSON.parse(localStorage.getItem("predict"));
        // let arr1 = localStorage.getItem("setting");
        // let arr2 = localStorage.getItem("predict");
        delete setting_json.file;//删除json中的key:value

        console.log(setting_json);
        // console.log(predict_array);
        // console.log(Array.isArray(setting_json));
        // console.log(Array.isArray(predict_array));

        predict_array.push(setting_json);//给predict_array后添加setting_json,返回的是数组的长度
        // console.log(predict_array);
        console.log("executing schedule...")
        const that = this;
        fetch(API + '/schedule', Headers(predict_array)).then(res => {
            if (res.status === 200) {
                return res.json();
            }
        }).then(function (json) {
            let length = json.length;
            let tablevalue = JSON.stringify(json.slice(0, length - 1));
            // console.log(data);
            that.setState({
                scheduleValue: tablevalue,
                chartData: JSON.stringify(json.slice(length - 1, length)),
                envSetting: {
                    startTime: setting_json.start_time,
                    endTime: setting_json.end_time
                }
            });
            localStorage.setItem("schedule_output", tablevalue);
            localStorage.setItem("statistic", JSON.stringify(json.slice(length - 1, length)));
        });
    };
    
    change = (key) => {
        this.setState({ activeKey: key });
    }

    logoClick = () => {
        window.location.href = 'http://localhost:3000';
    }
    render() {
        return (
            <div style={{ "backgroundColor": '#202743'}}>
                <div>
                    <img onClick={this.logoClick} src={bar} className='Yinlogo' />
                </div>
                <Tabs activeKey={this.state.activeKey} onChange={this.change} tabBarStyle={{color:'white'}}>
                    <TabPane style={{background:"#202743"}} tab="患者总览" key="1">
                        <div id={"editableTable"} className='predictOutput'>
                            <EditableTable pagination={{ pageSize: 10 }} scroll={{ y: 240 }} />
                        </div>
                        <div>
                            <Button onClick={this.handleClick} type="primary" style={{ marginBottom: 16 }} className="submit"> 开始调度 </Button>
                        </div>
                    </TabPane>
                    <TabPane tab="手术室调度排班表" key="2">
                        <Jia scheduleValue={this.state.scheduleValue} envSetting={this.state.envSetting}/>
                        <div style={{ width: "30%", display: "inline-block", marginLeft: "12%" }}>
                            <LineChart chartData = {this.state.chartData}/>
                        </div>
                        <div style={{ width: "30%", display: "inline-block", marginLeft: "12%" }}>
                            <LineChart2 chartData = {this.state.chartData}/>
                        </div>
                        <div style={{ marginLeft: "-5%", width: "80%", display: "inline-block" }}>
                            <Pie chartData = {this.state.chartData}/>
                        </div>
                    </TabPane>
                </Tabs>
            </div>
        );

    }
}

export default Yin;
