# Multi-Installation Support Proposal

## 🎯 **Problem Statement**
Field agents need to work on multiple installations simultaneously. Currently, each agent can only have one active installation per phone number.

## 💡 **Proposed Solution: DR-Based Session Switching**

### **Enhanced Workflow:**

1. **Agent starts first installation:**
   ```
   Agent: START
   Bot: Please provide DR number...
   Agent: DR0000001
   Bot: DR recorded, share location... [continues with DR0000001]
   ```

2. **Agent needs to start second installation:**
   ```
   Agent: DR0000002  [New DR number]
   Bot: 🔄 Switched to new installation DR0000002
        📋 Job ID: JOB_xxx_DR0000002
        📍 Please share location...
   ```

3. **Agent switches back to first installation:**
   ```
   Agent: DR0000001  [Existing DR number]  
   Bot: 🔄 Switched to DR0000001
        📊 Progress: 3/12 steps completed
        📷 Next: Step 4 - Home Entry Point...
   ```

### **New Commands:**
- **`LIST`** - Show all active installations
- **`DR1234567`** - Switch to/create installation with that DR
- **`STATUS DR1234567`** - Status of specific DR (optional)

### **Implementation Strategy:**

#### **Session Storage Enhancement:**
```json
{
  "+27640412391": {
    "agent_id": "27640412391",
    "phone_number": "+27640412391", 
    "current_dr": "DR0000001",
    "installations": {
      "DR0000001": {
        "job_id": "JOB_xxx_DR0000001",
        "current_step": 3,
        "completed_steps": {1: "path1", 2: "path2"},
        "dr_number": "DR0000001",
        "location_verified": true,
        "status": "active"
      },
      "DR0000002": {
        "job_id": "JOB_xxx_DR0000002", 
        "current_step": -1,
        "completed_steps": {},
        "dr_number": "DR0000002",
        "location_verified": false,
        "status": "active"
      }
    }
  }
}
```

#### **Key Logic Changes:**
1. **DR Input Handler**: Check if DR exists → switch, else create new
2. **Photo Handler**: Use current_dr to determine active installation
3. **Status Command**: Show current installation + option to list all
4. **LIST Command**: Show all active installations with progress

### **Benefits:**
✅ **Backward Compatible**: Existing single-installation workflow unchanged  
✅ **Intuitive**: Agents switch by entering DR numbers  
✅ **Flexible**: Support unlimited concurrent installations  
✅ **Simple**: Minimal UI changes required  
✅ **Clear Context**: Always shows which DR is active  

### **Example Multi-Installation Session:**
```
Agent: START
Bot: Please provide DR number...

Agent: DR0000001  
Bot: ✅ DR0000001 recorded, share location...
[Agent shares location, completes steps 1-3]

Agent: DR0000002  [Working on new drop]
Bot: 🔄 NEW installation DR0000002 started
     📋 Job ID: JOB_xxx_DR0000002  
     📍 Please share location...
[Agent shares location, starts step 1]

Agent: LIST
Bot: 📋 Active Installations:
     • DR0000001 - Step 4/12 (33% complete)
     • DR0000002 - Step 1/12 (0% complete)
     ▶️ Currently working on: DR0000002

Agent: DR0000001  [Switch back]
Bot: 🔄 Switched to DR0000001
     📊 Progress: 3/12 steps (25%)
     📷 Next: Step 4 - Home Entry Point...
```

### **Implementation Effort:**
- **Low Risk**: Builds on existing system
- **2-3 hours**: Modify session management + DR switching
- **Tested Approach**: Extend current DR input handler
- **User Friendly**: Natural workflow for field agents

Would you like me to implement this enhanced multi-installation support?