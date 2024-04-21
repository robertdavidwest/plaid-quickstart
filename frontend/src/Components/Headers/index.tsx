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
    isLoggedIn,
    linkToken,
    backend,
    linkTokenError,
  } = useContext(Context);

  return (
    <div className={styles.grid}>
      <h3 className={styles.title}>Spirit Cat</h3>
      <h4 className={styles.subtitle}>
        All of your transactions in one place
      </h4>
      <p className={styles.introPar}>
        With Spirit Cat, you can easily categorize and customize your
        spending habits. Know exactly how much you've spent and what on
        instantly. Effortlessly compare your spend month over month.
      </p>

      {isLoggedIn ? (
        <>
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
              <div className={styles.linkButton}>
                <Logout />
              </div>
            </>
            )}
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
