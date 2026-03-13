/******************************************************************************
 * @file rws.h
 * @brief Rear Wheel Steering - Interface Definition
 * @version 1.0.0
 * @author WeAgent Multi-Agent System
 * @date 2026-03-13
 * 
 * ASIL Level: D
 ******************************************************************************/

#ifndef RWS_H
#define RWS_H

#include "Std_Types.h"

/*============================================================================*
 * MACRO DEFINITIONS
 *============================================================================*/
#define RWS_CYCLE_TIME_MS               20U
#define RWS_MAX_ANGLE                   100     /* 10 deg * 10 */
#define RWS_MAX_RATE                    30      /* deg/s */
#define RWS_VEL_LOW_THRESHOLD           30      /* km/h */
#define RWS_VEL_HIGH_THRESHOLD          60      /* km/h */

/*============================================================================*
 * TYPE DEFINITIONS
 *============================================================================*/
typedef uint8_t Rws_StateType;
#define RWS_STATE_INIT                  0x00U
#define RWS_STATE_CALIBRATION           0x01U
#define RWS_STATE_STANDBY               0x02U
#define RWS_STATE_ACTIVE                0x03U
#define RWS_STATE_OPPOSITE_PHASE        0x04U
#define RWS_STATE_IN_PHASE              0x05U
#define RWS_STATE_DEAD_ZONE             0x06U
#define RWS_STATE_FAULT                 0x07U
#define RWS_STATE_CENTERING             0x08U
#define RWS_STATE_LOCKED                0x09U

/*============================================================================*
 * GLOBAL FUNCTIONS
 *============================================================================*/
extern void Rws_Init(void);
extern void Rws_MainFunction(void);
extern void Rws_ControlAlgorithm(sint16 frontAngle, uint16 vehicleSpeed, sint16 adasReq);
extern sint16 Rws_CalculateGain(uint16 vehicleSpeed);
extern void Rws_CenteringControl(void);
extern Rws_StateType Rws_GetState(void);

#endif /* RWS_H */
