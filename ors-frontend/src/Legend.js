import React from 'react';
import './Jia.css';
import { Tag } from 'antd';

function Legend() {
    return (<div style={{ marginLeft: "20px"}}>
        {/*<div className="OperationItemBody" style={{ width: "100px", background: "#508EEE", textAlign: 'center' }}>手术中</div>*/}
        {/*<div className="OperationItemBody" style={{ width: "100px", background: "#EB84C0", textAlign: 'center' }}>复苏中</div>*/}
        {/*<div className="OperationItemBody" style={{ width: "100px", background: "#74EDDA", textAlign: 'center' }}>清洁中</div>*/}
         <Tag color="#508EEE">手术中</Tag>
         <Tag color="#EB84C0">复苏中</Tag>
         <Tag color="#74EDDA">清洁中</Tag>
    </div>);
}

export default Legend;