/******************************************************************************
 * @file vdmc.h
 * @brief Vehicle Dynamic Motion Control - Interface Definition
 * @version 1.0.0
 * @author WeAgent Multi-Agent System
 * @date 2026-03-13
 * 
 * @copyright Copyright (c) 2026
 * 
 * AUTOSAR Standard: Classic Platform 4.4.0
 * ASIL Level: D
 ******************************************************************************/

#ifndef VDMC_H
#define VDMC_H

/*============================================================================*
 * INCLUDE HEADERS
 *============================================================================*/
#include "Std_Types.h"
#include "ComStack_Types.h"

/*============================================================================*
 * VERSION DEFINITION
 *============================================================================*/
#define VDMC_SW_MAJOR_VERSION           1
#define VDMC_SW_MINOR_VERSION           0
#define VDMC_SW_PATCH_VERSION           0

/*============================================================================*
 * MACRO DEFINITIONS
 *============================================================================*/
/* Control cycle time in milliseconds */
#define VDMC_CYCLE_TIME_MS              10U

/* Vehicle parameters */
#define VDMC_WHEELBASE_MM               2800U   /* Wheelbase in mm */
#define VDMC_TRACK_WIDTH_MM             1600U   /* Track width in mm */
#define VDMC_STEERING_RATIO             15U     /* Steering ratio */

/* Control limits */
#define VDMC_MAX_STEERING_ANGLE_DEG     720     /* Max steering angle in degrees */
#define VDMC_MAX_ACCELERATION_MSS       500     /* Max acceleration (0.01 m/s^2) */
#define VDMC_MAX_DECELERATION_MSS       1000    /* Max deceleration (0.01 m/s^2) */

/* Yaw control thresholds */
#define VDMC_YAW_RATE_ERROR_THRESHOLD   50      /* 5.0 deg/s * 10 */
#define VDMC_YAW_CONTROL_KP             1000    /* Proportional gain * 10 */
#define VDMC_YAW_CONTROL_KD             200     /* Derivative gain * 10 */

/*============================================================================*
 * TYPE DEFINITIONS
 *============================================================================*/

typedef uint8_t Vdmc_RequestSourceType;
#define VDMC_REQ_SOURCE_DRIVER          0x00U
#define VDMC_REQ_SOURCE_ADAS            0x01U
#define VDMC_REQ_SOURCE_ESC             0x02U
#define VDMC_REQ_SOURCE_AEB             0x03U

typedef uint8_t Vdmc_SystemStateType;
#define VDMC_STATE_INIT                 0x00U
#define VDMC_STATE_STANDBY              0x01U
#define VDMC_STATE_READY                0x02U
#define VDMC_STATE_NORMAL               0x03U
#define VDMC_STATE_DRIVER_ONLY          0x04U
#define VDMC_STATE_ADAS_ACTIVE          0x05U
#define VDMC_STATE_ESC_ACTIVE           0x06U
#define VDMC_STATE_DEGRADED             0x07U
#define VDMC_STATE_FAIL_SAFE            0x08U

typedef uint8_t Vdmc_FaultLevelType;
#define VDMC_FAULT_LEVEL_NONE           0x00U
#define VDMC_FAULT_LEVEL_1              0x01U
#define VDMC_FAULT_LEVEL_2              0x02U
#define VDMC_FAULT_LEVEL_3              0x03U

typedef struct
{
    sint16 steeringAngle;           /* Steering angle (0.1 deg) */
    sint16 steeringAngleRate;       /* Steering angle rate (deg/s) */
    uint8 accelPedalPos;            /* Accelerator pedal position (%) */
    uint8 brakePedalPos;            /* Brake pedal position (%) */
    boolean overrideFlag;           /* Driver override flag */
} Vdmc_DriverRequestType;

typedef struct
{
    sint16 latSteeringReq;          /* Lateral steering request (0.1 deg) */
    sint16 longAccelReq;            /* Longitudinal acceleration (0.01 m/s^2) */
    sint16 yawMomentReq;            /* Yaw moment request (0.1 Nm) */
    boolean active;                 /* ADAS active flag */
    boolean aebActive;              /* AEB active flag */
} Vdmc_ADASRequestType;

typedef struct
{
    uint16 vehicleSpeed;            /* Vehicle speed (0.1 km/h) */
    sint16 yawRate;                 /* Yaw rate (0.01 deg/s) */
    sint16 latAcc;                  /* Lateral acceleration (0.01 m/s^2) */
    sint16 longAcc;                 /* Longitudinal acceleration (0.01 m/s^2) */
    uint8 gearPos;                  /* Gear position */
} Vdmc_VehicleStateType;

typedef struct
{
    sint16 axReq;                   /* Longitudinal acceleration request */
    sint16 steeringAngleReq;        /* Steering angle request */
    sint16 yawMomentReq;            /* Yaw moment request */
    Vdmc_RequestSourceType source;  /* Request source */
} Vdmc_FinalRequestType;

/*============================================================================*
 * GLOBAL FUNCTION PROTOTYPES
 *============================================================================*/

/******************************************************************************
 * @brief Initialize VDMC module
 * @param none
 * @return none
 ******************************************************************************/
extern void Vdmc_Init(void);

/******************************************************************************
 * @brief Main cyclic function for VDMC (10ms cycle)
 * @param none
 * @return none
 ******************************************************************************/
extern void Vdmc_MainFunction(void);

/******************************************************************************
 * @brief Request arbitration logic
 * @param none
 * @return none
 ******************************************************************************/
extern void Vdmc_RequestArbitration(void);

/******************************************************************************
 * @brief Coordinated control for multiple actuators
 * @param vehicleState : Pointer to vehicle state structure
 * @return none
 ******************************************************************************/
extern void Vdmc_CoordinatedControl(const Vdmc_VehicleStateType* vehicleState);

/******************************************************************************
 * @brief Vehicle stability control
 * @param vehicleState : Pointer to vehicle state structure
 * @return none
 ******************************************************************************/
extern void Vdmc_StabilityControl(const Vdmc_VehicleStateType* vehicleState);

/******************************************************************************
 * @brief Get current system state
 * @param none
 * @return Current system state
 ******************************************************************************/
extern Vdmc_SystemStateType Vdmc_GetSystemState(void);

/******************************************************************************
 * @brief Get fault level
 * @param none
 * @return Current fault level
 ******************************************************************************/
extern Vdmc_FaultLevelType Vdmc_GetFaultLevel(void);

/******************************************************************************
 * @brief Set driver request input
 * @param driverReq : Pointer to driver request structure
 * @return none
 ******************************************************************************/
extern void Vdmc_SetDriverRequest(const Vdmc_DriverRequestType* driverReq);

/******************************************************************************
 * @brief Set ADAS request input
 * @param adasReq : Pointer to ADAS request structure
 * @return none
 ******************************************************************************/
extern void Vdmc_SetADASRequest(const Vdmc_ADASRequestType* adasReq);

/******************************************************************************
 * @brief Get final arbitration output
 * @param finalReq : Pointer to final request structure to be filled
 * @return none
 ******************************************************************************/
extern void Vdmc_GetFinalRequest(Vdmc_FinalRequestType* finalReq);

#endif /* VDMC_H */
