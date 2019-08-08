import React, {Component} from 'react';
import './Jia.css';
import { Tooltip, Drawer, Button } from 'antd';
import { Bar as BarChart, Doughnut } from 'react-chartjs-2';
import API from "./utils/api";

const unitPx = 15;

class OperationItem extends Component {
    state = { visible: false };

    showDrawer = () => {
        this.setState({
            visible: true,
        });
    };

    onClose = () => {
        this.setState({
            visible: false,
        });
    };
    render() {
        return (<div className="OperationItem"
            style={{ left: this.props.beginIndex * unitPx + "px" }}>
            <div className="TimeTag">
            </div>
            <Tooltip placement="topLeft" title={this.props.secondInfo}>
                <div className="OperationItemBody" onClick={this.showDrawer} style={{ width: this.props.operationDuration * unitPx + "px" }}>
                    {this.props.patientName}
                </div>
            </Tooltip>
            <div className="OperationItemBody"
                style={{ width: this.props.recoverDuration * unitPx + "px", background: '#EB84C0' }}>
            </div>
            <div className="OperationItemBody"
                style={{ width: this.props.cleanDuration * unitPx + "px", background: '#74EDDA' }}>
            </div>
            <div className="TimeTag">
            </div>
            <Drawer
                title="详细信息"
                placement="right"
                closable={false}
                onClose={this.onClose}
                visible={this.state.visible}
            >
                <p>{this.props.thirdInfo}</p>
            </Drawer>
        </div>);
    }
}

function OperationScheduleTable(props) {
        return (<div>
            <div className={"OperationSchedule"}>
                <table style={{tableLayout: "fixed", width: "200px"}}>
                    {/*-------------------横轴------------------*/}
                    <thead className={"stickyRow"}>
                        <tr className={"stickyRow"}>
                            <th className={"stickyRow bedInfo scheduleHeader"} style={{zIndex: 4}}>{null}</th>
                            {[...Array(64).keys()].map(x => {
                                return <th className={"stickyRow scheduleHeader quarterCell"} key={x}>
                                    <div style={{width: "100%", height: "100%", position: "relative"}}>
                                        <p className={"timeTag"}>
                                            {!(x % 2) ? (("0" + (Math.floor(x / 4) + 8)).slice(-2) + ":" + (!(x % 4) ? "00" : "30")) : null}
                                        </p>
                                        {!(x % 4) ? <div className={"timePoint"}>{null}</div> : null}
                                    </div>
                                </th>
                            })}
                        </tr>
                    </thead>
                    {/*-------------------横轴------------------*/}
                    <tbody>
                        {props.schedules.map((bedSchedule, bedIdx) => {
                            return ([
                                <tr key={"space" + bedIdx} className={"stickyRow"}>
                                    <td className={"bedInfo spaceRow"}>{null}</td>
                                    {[...Array(64).keys()].map(y => {
                                        return <td className={"quarterCell spaceRow"} key={y}>{null}</td>
                                    })}
                                </tr>,
                                <tr key={"data" + bedIdx} className={"stickyRow"}>
                                    {/*-------纵轴-------*/}
                                    <td className={"bedInfo"}>{bedSchedule.roomInfo}</td>
                                    {/*-------纵轴-------*/}
                                    <td className={"quarterCell dataRow"}>
                                        <div className={"BedScheduleTd"}>
                                            {
                                                bedSchedule.operation.map((x, y) => {
                                                    return <OperationItem key={y}
                                                                          patientName={x.patientName}
                                                                          beginIndex={x.beginIndex}
                                                                          operationDuration={x.operationDuration}
                                                                          secondInfo={x.secondInfo}
                                                                          thirdInfo={x.thirdInfo}
                                                                          recoverDuration={x.recoverDuration}
                                                                          cleanDuration={x.recoverDuration} />
                                                })
                                            }
                                        </div>
                                    </td>
                                    {[...Array(63).keys()].map(y => {
                                        return <td className={"quarterCell dataRow"} key={y}>{null}</td>
                                    })}
                                </tr>
                            ])
                        })}
                        <tr className={"stickyRow"}>
                            <td className={"bedInfo"}>{null}</td>
                            {[...Array(64).keys()].map(y => {
                                return <td className={"quarterCell spaceRow"} key={y}>{null}</td>
                            })}
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>)
}

class Jia extends Component {
    constructor(props) {
        super(props);
    };
    
    preview = () => { // 预览
        let myscheduleValue = JSON.parse(this.props.scheduleValue);
        let values1 = myscheduleValue.sort(this.compare("orId", "startTime"));
        console.log(values1);
        fetch(API + '/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=UTF-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
            },
            responseType: 'blob',
            body: JSON.stringify(values1)
        }).then(res => {
            if (res.status === 200) {
                return res.blob()
            }
        }).then(function (blob) {
            let blobUrl = window.URL.createObjectURL(blob);
            window.open(blobUrl);
        });
    };

    compare(property1, property2) {
        return function (obj1, obj2) {
            var value1 = obj1[property1];
            var value2 = obj2[property1];
            if (value1 === value2) {
                var a = obj1[property2].split(":");
                var b = obj2[property2].split(":");
                let x = parseInt(a[0]) * 60 + parseInt(a[1]);
                let y = parseInt(b[0]) * 60 + parseInt(b[1]);
                return x - y;
            }
            else {
                return value1 - value2;     // 升序
            }
        }
    }

    genSchedules(data) { // data: values1
        if (data.length == 0) { return [] }
        let orid = data[0]['orId'];
        let index = 0;
        let result = [{ 'roomInfo': 'Room ' + orid, 'operation': [] }];
        for (var dataindex in data) {
            let x = data[dataindex];
            console.log(x);
            console.log(result);
            console.log('---------------------\n');
            let tmp = {};
            tmp['patientName'] = x['name'] + " " + x['startTime'];
            tmp['secondInfo'] = x['name'] + " " + x['startTime'] + " " + x['predTime'] + "分钟 " + x['operatingName'];
            tmp['thirdInfo'] = "就诊号" + x['id'] + " " + x['name'] + " " + x['startTime'] + " " + x['predTime'] + "分钟 " + x['operatingName'];
            let ti = x['startTime'].split(":");
            tmp['beginIndex'] = (parseInt(ti[0]) * 60 + parseInt(ti[1]) - 480) / 5;
            tmp['operationDuration'] = x['predTime'] / 5;
            tmp['recoverDuration'] = x['recoverDuration'] / 5;
            tmp['cleanDuration'] = x['cleanDuration'] / 5;

            if (x['orId'] == orid) {
                result[index]['operation'].push(tmp);
            }
            else {
                orid = x['orId'];
                index += 1;
                result.push({
                    'roomInfo': 'Room ' + x['orId'],
                    'operation': [tmp]
                });
            }
        }
        return result;
    }

    render(){
        let values = [ // 数据从localStorage中取出来
            {
                "key": 3, // 表格编号
                "id": "1",
                "name": "张三",
                "gender": "男",
                "age": "70",
                "department": "心血管科",
                "operatingName": "心脏搭桥手术",
                "anaesthetic": "全身麻醉",
                "doctorName": "李四",
                "predTime": 120, // 分钟
                "orId": 1, //从1开始
                "startTime": "15:30",
                "recoverDuration": 20, // 分钟
                "cleanDuration": 20 // 分钟
            },
            {
                "key": 4,
                "id": "2",
                "name": "王二",
                "gender": "女",
                "age": "23",
                "department": "妇产科",
                "operatingName": "剖腹产手术",
                "anaesthetic": "全身麻醉",
                "doctorName": "王小二",
                "predTime": 100,
                "orId": 2,
                "startTime": "15:00",
                "recoverDuration": 10,
                "cleanDuration": 30
            },
            {
                "key": 1,
                "id": "1",
                "name": "李一",
                "gender": "男",
                "age": "50",
                "department": "心血管科",
                "operatingName": "心脏搭桥手术",
                "anaesthetic": "全身麻醉",
                "doctorName": "王五",
                "predTime": 100,
                "orId": 1,
                "startTime": "8:30",
                "recoverDuration": 20,
                "cleanDuration": 30
            },
            {
                "key": 2,
                "id": "1",
                "name": "赵赵",
                "gender": "男",
                "age": "50",
                "department": "心血管科",
                "operatingName": "心脏搭桥手术",
                "anaesthetic": "全身麻醉",
                "doctorName": "王五",
                "predTime": 100,
                "orId": 1,
                "startTime": "10:30",
                "recoverDuration": 20,
                "cleanDuration": 30
            }
        ];
        // console.log(this.props.scheduleValue);
        // console.log(typeof (this.props.scheduleValue));
        let myscheduleValue = JSON.parse(this.props.scheduleValue);
        let values1 = myscheduleValue.sort(this.compare("orId", "startTime"));
        // let values1 = values.sort(this.compare("orId", "startTime"));
        let scheds = this.genSchedules(values1);
        return (
            <div>
                <OperationScheduleTable schedules={scheds} />
                <Button type="primary" onClick={this.preview} style={{marginLeft:"95%"}}>预览</Button>
            </div>
        )
    };
}

export default Jia;
