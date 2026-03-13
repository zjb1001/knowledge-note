/******************************************************************************
 * @file icc.h
 * @brief Integrated Chassis Control - Interface Definition
 * @version 1.0.0
 * @author WeAgent Multi-Agent System
 * @date 2026-03-13
 * 
 * ASIL Level: D
 ******************************************************************************/

#ifndef ICC_H
#define ICC_H

#include "Std_Types.h"

/*============================================================================*
 * MACRO DEFINITIONS
 *============================================================================*/
#define ICC_CYCLE_TIME_MS               10U
#define ICC_MAX_REGEN_DECELERATION      30      /* 0.1g = 0.98 m/s^2 * 10 */
#define ICC_MAX_HYDRAULIC_PRESSURE      200     /* 20 MPa * 10 */
#define ICC_RAMP_RATE_LIMIT             50      /* m/s^3 * 10 */

/*============================================================================*
 * TYPE DEFINITIONS
 *============================================================================*/
typedef uint8_t Icc_StateType;
#define ICC_STATE_INIT                  0x00U
#define ICC_STATE_STANDBY               0x01U
#define ICC_STATE_READY                 0x02U
#define ICC_STATE_REGEN_ONLY            0x03U
#define ICC_STATE_BLENDED               0x04U
#define ICC_STATE_HYDRAULIC_ONLY        0x05U
#define ICC_STATE_ESC_ACTIVE            0x06U
#define ICC_STATE_DEGRADED              0x07U
#define ICC_STATE_FAIL_SAFE             0x08U

typedef struct
{
    sint16 motorTorqueReq;          /* Motor torque request (0.1 Nm) */
    uint16 hydraulicPressureReq;    /* Hydraulic pressure request (0.1 MPa) */
    uint8 brakeForceDistribution[4]; /* FL, FR, RL, RR brake force (%) */
    boolean regenActive;            /* Regeneration active flag */
} Icc_OutputType;

/*============================================================================*
 * GLOBAL FUNCTIONS
 *============================================================================*/
extern void Icc_Init(void);
extern void Icc_MainFunction(void);
extern void Icc_BrakeForceDistribution(sint16 axReq, const void* vehicleState);
extern void Icc_ESCControl(sint16 yawMomentReq, const void* vehicleState);
extern Icc_StateType Icc_GetState(void);

#endif /* ICC_H */
