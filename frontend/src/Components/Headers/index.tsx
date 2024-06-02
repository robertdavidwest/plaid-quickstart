import React, { useContext } from "react";
import Callout from "plaid-threads/Callout";
import Button from "plaid-threads/Button";
import InlineLink from "plaid-threads/InlineLink";

import Link from "../Link";
import Context from "../../Context";
import Signup from "../Signup";
import Logout from "../Logout";
import Signin from "../Signin";

import styles from "./index.module.scss";

const Header = () => {
  const {
    userFirstName,
    isLoggedIn,
    linkToken,
    backend,
    linkTokenError,
  } = useContext(Context);
  const welcome_msg = userFirstName ? `Welcome back, ${userFirstName}!` : "Welcome!";

  return (
    <div className={styles.grid}>
      <h3 className={styles.title}>Spirit Cat</h3>
      <h4 className={styles.subtitle}>
        No Thrills. Simple Text Alerts via Telegram.
      </h4>
      {!isLoggedIn ? (
        <p className={styles.introPar}>
          In our modern world in can be so difficult to keep track of our
          spending, or even, to know how much money we even have in a given 
          moment. 
          <br />
          <br />
          Spirit Cat solves this without trying to sell you anything
          and without overloading you with pie charts and graphs.
          <br />
          What is my balance?
          <br />
          How much did I spend so far this month?
          <br />
          <br />
          Take control of your finances with Spirit Cat. -- Sign up today!
        </p>
      ) : null}
      {isLoggedIn ? (
        <>
          <h4 className={styles.subtitle}>
            {welcome_msg}
          </h4>
          <p className={styles.introPar}>
            Follow these steps to get started:
            <ol>
              <li>
                To receive daily text alerts, 
                login to your Telegram account and start a chat with 
                 <strong>@SpiritCat_bot</strong>. After you've initiated the chat, we'll
                be able to message you there going forward.
              </li>
              <li>
                To receive monthly text alerts, 
                login to your Telegram account and start a chat with 
                 <strong>@SpiritCatMonthly_bot</strong>. After you've initiated the chat, we'll
                be able to message you there going forward.
              </li>
              <li>
                Click the button below to link a bank account with Plaid (
                You can link as many accounts as you'd like!)
              </li>
              <li>
                That it! Once you've linked your account, you can start receiving text
                alerts each day.
              </li>
            </ol>
          Note : This is a proof of concept app, which is fully functional, 
          but not very configurable yet for the end user. Eventually there
          will be a more sophisticated user interface to allow you to
          set your own preferences in terms of what information you'd like
          to receive each day.
          </p>
          {/* message if backend is not running and there is no link token */}
          {!backend ? (
            <Callout warning>
              Unable to fetch link_token: please make sure your backend server
              is running and that your .env file has been configured with your
              <code>PLAID_CLIENT_ID</code> and <code>PLAID_SECRET</code>.
            </Callout>
          ) : /* message if backend is running and there is no link token */
            linkToken == null && backend ? (
              <Callout warning>
                <div>
                  Unable to fetch link_token: please make sure your backend server
                  is running and that your .env file has been configured
                  correctly.
                </div>
                <div>
                  If you are on a Windows machine, please ensure that you have
                  cloned the repo with{" "}
                  <InlineLink
                    href="https://github.com/plaid/quickstart#special-instructions-for-windows"
                    target="_blank"
                  >
                    symlinks turned on.
                  </InlineLink>{" "}
                  You can also try checking your{" "}
                  <InlineLink
                    href="https://dashboard.plaid.com/activity/logs"
                    target="_blank"
                  >
                    activity log
                  </InlineLink>{" "}
                  on your Plaid dashboard.
                </div>
                <div>
                  Error Code: <code>{linkTokenError.error_code}</code>
                </div>
                <div>
                  Error Type: <code>{linkTokenError.error_type}</code>{" "}
                </div>
                <div>Error Message: {linkTokenError.error_message}</div>
              </Callout>
            ) : linkToken === "" ? (
              <div className={styles.linkButton}>
                <Button large disabled>
                  Loading...
                </Button>
              </div>
            ) : (<>
              <div className={styles.linkButton}>
                <Link />
              </div>
            </>
            )}
          <div className={styles.linkButton}>
            <Logout />
          </div>
        </>
      ) : (
        <>
          <div className={styles.linkButton}>
            <Signup />
          </div>
          <div className={styles.linkButton}>
            <Signin />
          </div>
        </>
      )}
    </div>
  );
};

Header.displayName = "Header";

export default Header;
